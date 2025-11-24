from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, time
import json
import os

import sys
sys.path.append('..')
from models.usuario import Usuario
from models.mensaje import Mensaje
from models.conocimiento import (
    BaseConocimiento, Horario, Evento, Carrera, DiaSemana
)
from services.procesador_lenguaje import ProcesadorLenguajeNatural
from services.gestor_respuestas import GestorRespuestas
from services.base_datos import BaseDatos

try:
    from services.google_sheets_reader import GoogleSheetsReader
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    print("⚠️  Google Sheets Reader no disponible. Instala las dependencias.")
    GOOGLE_SHEETS_AVAILABLE = False

app = FastAPI(
    title="Chatbot Universitario API",
    description="API REST para chatbot universitario con WhatsApp y Google Sheets",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

base_datos = BaseDatos()
base_conocimiento = BaseConocimiento()
gestor_respuestas = GestorRespuestas(base_conocimiento)

import os

print(f"🔍 DEBUG: Buscando credentials.json...")
print(f"   Ruta esperada: api/credentials.json")
print(f"   Existe: {os.path.exists('api/credentials.json')}")
print(f"   Directorio actual: {os.getcwd()}")
print(f"   Archivos en api/: {os.listdir('api/') if os.path.exists('api/') else 'CARPETA NO EXISTE'}")

import json
import tempfile
import os
import base64

google_sheets_reader = None
if GOOGLE_SHEETS_AVAILABLE:
    try:
        # Intenta leer archivo local primero
        CREDENTIALS_FILE = "api/credentials.json"
        
        if not os.path.exists(CREDENTIALS_FILE):
            # Si no existe, intenta variable de entorno
            creds_b64 = os.getenv("GOOGLE_CREDENTIALS_B64")
            if creds_b64:
                # Decodificar base64
                creds_json = base64.b64decode(creds_b64).decode('utf-8')
                # Crear archivo temporal
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                    f.write(creds_json)
                    CREDENTIALS_FILE = f.name
                    print(f"✅ Credenciales desde base64")
        
        if os.path.exists(CREDENTIALS_FILE):
            SHEET_ID = os.getenv("GOOGLE_SHEETS_ID", "1nEuZLDuowW5d9Li-91fO3DObAXTsuPYtTZM5vGpn_qo")
            google_sheets_reader = GoogleSheetsReader(CREDENTIALS_FILE, SHEET_ID)
            print("✅ Google Sheets Reader inicializado")
        else:
            print("⚠️ No credentials found")
            google_sheets_reader = None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        google_sheets_reader = None

class MensajeEntrada(BaseModel):
    telefono: str
    contenido: str
    nombre: Optional[str] = None
    horarios_sheets: Optional[List[Dict[str, Any]]] = None
    eventos_sheets: Optional[List[Dict[str, Any]]] = None
    carreras_sheets: Optional[List[Dict[str, Any]]] = None

class RespuestaAPI(BaseModel):
    success: bool
    respuesta: str
    usuario: Optional[dict] = None
    tipo_mensaje: Optional[str] = None

def cargar_datos_desde_sheets(horarios: List[Dict], eventos: List[Dict], carreras: List[Dict]):
    
    print("\n" + "="*60)
    print("📊 CARGANDO DATOS DESDE GOOGLE SHEETS")
    print("="*60)
    
    base_conocimiento.horarios.clear()
    base_conocimiento.eventos.clear()
    base_conocimiento.carreras.clear()
    
    if horarios:
        print(f"\n📅 Procesando {len(horarios)} horarios...")
        for h in horarios:
            try:
                dias_str = str(h.get('Dias', '')).lower()
                dias_lista = []
                
                if 'lunes' in dias_str and 'viernes' in dias_str:
                    dias_lista = [DiaSemana.LUNES, DiaSemana.MARTES, DiaSemana.MIERCOLES, 
                                 DiaSemana.JUEVES, DiaSemana.VIERNES]
                else:
                    if 'lunes' in dias_str: dias_lista.append(DiaSemana.LUNES)
                    if 'martes' in dias_str: dias_lista.append(DiaSemana.MARTES)
                    if 'miercoles' in dias_str or 'miércoles' in dias_str: dias_lista.append(DiaSemana.MIERCOLES)
                    if 'jueves' in dias_str: dias_lista.append(DiaSemana.JUEVES)
                    if 'viernes' in dias_str: dias_lista.append(DiaSemana.VIERNES)
                    if 'sabado' in dias_str or 'sábado' in dias_str: dias_lista.append(DiaSemana.SABADO)
                    if 'domingo' in dias_str: dias_lista.append(DiaSemana.DOMINGO)
                
                if not dias_lista:
                    dias_lista = [DiaSemana.LUNES]
                
                hora_inicio_str = str(h.get('Hora_Inicio', '08:00'))
                hora_fin_str = str(h.get('Hora_Fin', '20:00'))
                
                h_inicio_parts = hora_inicio_str.split(':')
                h_fin_parts = hora_fin_str.split(':')
                
                h_inicio = time(int(h_inicio_parts[0]), int(h_inicio_parts[1]) if len(h_inicio_parts) > 1 else 0)
                h_fin = time(int(h_fin_parts[0]), int(h_fin_parts[1]) if len(h_fin_parts) > 1 else 0)
                
                horario = Horario(
                    servicio=str(h.get('Servicio', 'Servicio')),
                    dias=dias_lista,
                    hora_inicio=h_inicio,
                    hora_fin=h_fin,
                    notas=str(h.get('Notas', ''))
                )
                base_conocimiento.agregar_horario(horario)
                print(f"   ✅ {horario.servicio}")
                
            except Exception as e:
                print(f"   ❌ Error procesando horario: {e}")
    
    if eventos:
        print(f"\n🎉 Procesando {len(eventos)} eventos...")
        for e in eventos:
            try:
                fecha_inicio_str = str(e.get('Fecha_Inicio', ''))
                fecha_fin_str = str(e.get('Fecha_Fin', ''))
                
                if fecha_inicio_str and fecha_inicio_str != '':
                    try:
                        if '/' in fecha_inicio_str:
                            fecha_inicio = datetime.strptime(fecha_inicio_str, '%d/%m/%Y')
                            fecha_fin = datetime.strptime(fecha_fin_str, '%d/%m/%Y') if fecha_fin_str else fecha_inicio
                        else:
                            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
                            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d') if fecha_fin_str else fecha_inicio
                        
                        evento = Evento(
                            nombre=str(e.get('Nombre', 'Evento')),
                            descripcion=str(e.get('Descripcion', '')),
                            fecha_inicio=fecha_inicio,
                            fecha_fin=fecha_fin,
                            lugar=str(e.get('Lugar', '')),
                            categoria=str(e.get('Categoria', 'General'))
                        )
                        base_conocimiento.agregar_evento(evento)
                        print(f"   ✅ {evento.nombre}")
                    except:
                        print(f"   ⚠️  Formato de fecha inválido: {fecha_inicio_str}")
                        
            except Exception as err:
                print(f"   ❌ Error procesando evento: {err}")
    
    if carreras:
        print(f"\n🎓 Procesando {len(carreras)} carreras...")
        for c in carreras:
            try:
                duracion = c.get('Duracion_Semestres', 8)
                if isinstance(duracion, str):
                    duracion = int(duracion)
                
                carrera = Carrera(
                    nombre=str(c.get('Nombre', 'Carrera')).strip(),
                    duracion_semestres=duracion,
                    descripcion=str(c.get('Descripción', '') or c.get('Descripción ', '')).strip(),
                    coordinador=str(c.get('Coordinador', '')).strip()
                )
                base_conocimiento.agregar_carrera(carrera)
                print(f"   ✅ {carrera.nombre}")
                
            except Exception as e:
                print(f"   ❌ Error procesando carrera: {e}")
    
    print("\n" + "="*60)
    print(f"✅ DATOS CARGADOS: {len(base_conocimiento.horarios)} horarios, "
          f"{len(base_conocimiento.eventos)} eventos, {len(base_conocimiento.carreras)} carreras")
    print("="*60 + "\n")


@app.get("/")
async def root():
    return {
        "mensaje": "API Chatbot Universitario con Google Sheets",
        "version": "2.1.0",
        "status": "activo",
        "google_sheets_disponible": GOOGLE_SHEETS_AVAILABLE and google_sheets_reader is not None,
        "datos_cargados": {
            "horarios": len(base_conocimiento.horarios),
            "eventos": len(base_conocimiento.eventos),
            "carreras": len(base_conocimiento.carreras)
        }
    }

@app.post("/webhook-whatsapp")
async def webhook_whatsapp_twilio(request: Request):

    try:
        form_data = await request.form()
        
        from_number = form_data.get('From', '') 
        message_body = form_data.get('Body', '')
        message_sid = form_data.get('MessageSid', '')
        
        telefono = from_number.replace('whatsapp:', '') if from_number else ''
        
        print(f"\n{'='*60}")
        print(f"📱 MENSAJE DE WHATSAPP (TWILIO)")
        print(f"{'='*60}")
        print(f"De: {telefono}")
        print(f"Mensaje: {message_body}")
        print(f"MessageSID: {message_sid}")
        print(f"{'='*60}\n")
        
        if not telefono or not message_body:
            return Response(
                content="""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Error: Faltan datos requeridos</Message>
</Response>""",
                media_type="application/xml"
            )
        
        if google_sheets_reader:
            try:
                print("📊 Leyendo datos de Google Sheets...")
                all_data = google_sheets_reader.get_all_data()
                cargar_datos_desde_sheets(
                    all_data['horarios'],
                    all_data['eventos'],
                    all_data['carreras']
                )
            except Exception as e:
                print(f"⚠️  Error leyendo Google Sheets: {e}")
        
        usuario = base_datos.obtener_usuario(telefono)
        if not usuario:
            usuario = Usuario(telefono=telefono, nombre=telefono)
            base_datos.guardar_usuario(usuario)
            print(f"✅ Usuario nuevo: {telefono}")
        else:
            usuario.actualizar_interaccion()
            base_datos.guardar_usuario(usuario)
        
        mensaje_usuario = Mensaje(telefono=telefono, contenido=message_body, es_bot=False)
        base_datos.guardar_mensaje(mensaje_usuario)
        
        respuesta_texto = gestor_respuestas.generar_respuesta(mensaje_usuario)
        print(f"🤖 Respuesta: {respuesta_texto[:100]}...\n")
        
        mensaje_bot = Mensaje(telefono=telefono, contenido=respuesta_texto, es_bot=True)
        base_datos.guardar_mensaje(mensaje_bot)
        
        xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{respuesta_texto}</Message>
</Response>"""
        
        return Response(content=xml_response, media_type="application/xml")
        
    except Exception as e:
        print(f"❌ Error en webhook WhatsApp: {e}")
        import traceback
        traceback.print_exc()
        
        xml_error = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Disculpa, hubo un error procesando tu mensaje. Por favor intenta de nuevo.</Message>
</Response>"""
        
        return Response(content=xml_error, media_type="application/xml")

@app.post("/webhook", response_model=RespuestaAPI)
async def webhook_whatsapp(datos: MensajeEntrada):
   
    try:
        print(f"\n📨 Mensaje de {datos.telefono}: {datos.contenido}")
        
        if datos.horarios_sheets or datos.eventos_sheets or datos.carreras_sheets:
            cargar_datos_desde_sheets(
                datos.horarios_sheets or [],
                datos.eventos_sheets or [],
                datos.carreras_sheets or []
            )
        
        telefono = datos.telefono
        contenido = datos.contenido
        
        usuario = base_datos.obtener_usuario(telefono)
        if not usuario:
            usuario = Usuario(telefono=telefono, nombre=datos.nombre)
            base_datos.guardar_usuario(usuario)
            print(f"✅ Usuario nuevo: {telefono}")
        else:
            usuario.actualizar_interaccion()
            base_datos.guardar_usuario(usuario)
        
        mensaje_usuario = Mensaje(telefono=telefono, contenido=contenido, es_bot=False)
        base_datos.guardar_mensaje(mensaje_usuario)
        
        respuesta_texto = gestor_respuestas.generar_respuesta(mensaje_usuario)
        print(f"🤖 Respuesta: {respuesta_texto[:80]}...")
        
        mensaje_bot = Mensaje(telefono=telefono, contenido=respuesta_texto, es_bot=True)
        base_datos.guardar_mensaje(mensaje_bot)
        
        return RespuestaAPI(
            success=True,
            respuesta=respuesta_texto,
            usuario=usuario.to_dict(),
            tipo_mensaje=mensaje_usuario.tipo.value if mensaje_usuario.tipo else None
        )
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/webhook-raw")
async def webhook_raw(request: Request):
    try:
        body = await request.json()
        
        print(f"\n📨 Datos RAW recibidos:")
        print(json.dumps(body, indent=2))
        
        telefono = body.get('telefono', '')
        contenido = body.get('contenido', '')
        nombre = body.get('nombre', '')
        
        horarios = body.get('horarios_sheets', [])
        eventos = body.get('eventos_sheets', [])
        carreras = body.get('carreras_sheets', [])
        
        if horarios or eventos or carreras:
            cargar_datos_desde_sheets(horarios, eventos, carreras)
        
        usuario = base_datos.obtener_usuario(telefono)
        if not usuario:
            usuario = Usuario(telefono=telefono, nombre=nombre)
            base_datos.guardar_usuario(usuario)
        else:
            usuario.actualizar_interaccion()
            base_datos.guardar_usuario(usuario)
        
        mensaje_usuario = Mensaje(telefono=telefono, contenido=contenido, es_bot=False)
        base_datos.guardar_mensaje(mensaje_usuario)
        
        respuesta_texto = gestor_respuestas.generar_respuesta(mensaje_usuario)
        
        mensaje_bot = Mensaje(telefono=telefono, contenido=respuesta_texto, es_bot=True)
        base_datos.guardar_mensaje(mensaje_bot)
        
        return {
            "success": True,
            "respuesta": respuesta_texto,
            "usuario": usuario.to_dict()
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@app.get("/usuarios/{telefono}")
async def obtener_usuario(telefono: str):
    usuario = base_datos.obtener_usuario(telefono)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario.to_dict()

@app.get("/historial/{telefono}")
async def obtener_historial(telefono: str, limite: int = 20):
    mensajes = base_datos.obtener_mensajes_usuario(telefono, limite)
    return {
        "telefono": telefono,
        "total_mensajes": len(mensajes),
        "mensajes": [m.to_dict() for m in mensajes]
    }

@app.get("/estadisticas")
async def obtener_estadisticas():
    return base_datos.obtener_estadisticas()

@app.get("/eventos")
async def listar_eventos(proximos_dias: int = 60):
    eventos = base_conocimiento.obtener_eventos_proximos(proximos_dias)
    return {
        "total": len(eventos),
        "eventos": [
            {
                "nombre": e.nombre,
                "descripcion": e.descripcion,
                "fecha_inicio": e.fecha_inicio.isoformat(),
                "fecha_fin": e.fecha_fin.isoformat(),
                "lugar": e.lugar,
                "categoria": e.categoria,
                "dias_faltantes": e.dias_para_evento()
            }
            for e in eventos
        ]
    }

@app.get("/horarios")
async def listar_horarios():
    return {
        servicio: {
            "dias": [d.value for d in horario.dias],
            "hora_inicio": horario.hora_inicio.strftime("%H:%M"),
            "hora_fin": horario.hora_fin.strftime("%H:%M"),
            "notas": horario.notas
        }
        for servicio, horario in base_conocimiento.horarios.items()
    }

@app.get("/carreras")
async def listar_carreras():
    return {
        nombre: {
            "duracion_semestres": carrera.duracion_semestres,
            "descripcion": carrera.descripcion,
            "coordinador": carrera.coordinador
        }
        for nombre, carrera in base_conocimiento.carreras.items()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "google_sheets_disponible": GOOGLE_SHEETS_AVAILABLE and google_sheets_reader is not None,
        "datos_en_memoria": {
            "horarios": len(base_conocimiento.horarios),
            "eventos": len(base_conocimiento.eventos),
            "carreras": len(base_conocimiento.carreras)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)