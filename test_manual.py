"""
Script para probar el chatbot sin necesidad de WhatsApp o n8n
Útil para desarrollo y debugging
"""

import sys
sys.path.append('.')

from models.usuario import Usuario
from models.mensaje import Mensaje
from models.conocimiento import BaseConocimiento, Horario, Evento, Carrera, DiaSemana
from services.procesador_lenguaje import ProcesadorLenguajeNatural
from services.gestor_respuestas import GestorRespuestas
from services.base_datos import BaseDatos
from datetime import datetime, time

def inicializar_sistema():
    """Inicializa todos los componentes del sistema"""
    print("🚀 Inicializando sistema...")
    
    # Base de datos
    bd = BaseDatos()
    
    # Base de conocimiento
    bc = BaseConocimiento()
    
    # Agregar horarios
    bc.agregar_horario(Horario(
        servicio="Biblioteca",
        dias=[DiaSemana.LUNES, DiaSemana.MARTES, DiaSemana.MIERCOLES, 
              DiaSemana.JUEVES, DiaSemana.VIERNES],
        hora_inicio=time(8, 0),
        hora_fin=time(20, 0),
        notas="Sábados de 9:00 a 14:00"
    ))
    
    bc.agregar_horario(Horario(
        servicio="Laboratorios",
        dias=[DiaSemana.LUNES, DiaSemana.MARTES, DiaSemana.MIERCOLES, 
              DiaSemana.JUEVES, DiaSemana.VIERNES],
        hora_inicio=time(7, 0),
        hora_fin=time(21, 0),
        notas="Requiere reservación previa"
    ))
    
    bc.agregar_horario(Horario(
        servicio="Comedor",
        dias=[DiaSemana.LUNES, DiaSemana.MARTES, DiaSemana.MIERCOLES, 
              DiaSemana.JUEVES, DiaSemana.VIERNES],
        hora_inicio=time(7, 30),
        hora_fin=time(16, 0),
        notas="Desayuno: 7:30-10:00, Comida: 13:00-16:00"
    ))
    
    # Agregar eventos
    bc.agregar_evento(Evento(
        nombre="Exámenes Finales",
        descripcion="Periodo de exámenes finales del semestre",
        fecha_inicio=datetime(2025, 11, 25),
        fecha_fin=datetime(2025, 11, 29),
        lugar="Aulas asignadas",
        categoria="Académico"
    ))
    
    bc.agregar_evento(Evento(
        nombre="Inscripciones Semestre Primavera 2026",
        descripcion="Periodo de inscripción para el semestre de primavera",
        fecha_inicio=datetime(2025, 12, 1),
        fecha_fin=datetime(2025, 12, 15),
        lugar="En línea y control escolar",
        categoria="Académico"
    ))
    
    # Agregar carreras
    carrera_sistemas = Carrera(
        nombre="Ingeniería en Sistemas Computacionales",
        duracion_semestres=9,
        descripcion="Formamos profesionales capaces de diseñar, desarrollar e implementar soluciones tecnológicas innovadoras.",
        coordinador="Dr. Juan Pérez García"
    )
    bc.agregar_carrera(carrera_sistemas)
    
    # Agregar trámites
    bc.agregar_tramite(
        "credencial",
        "📋 *CREDENCIAL ESTUDIANTIL*\n"
        "Requisitos:\n"
        "• 2 fotografías tamaño infantil\n"
        "• Comprobante de pago ($50)\n"
        "• Identificación oficial\n\n"
        "Lugar: Control Escolar\n"
        "Tiempo de entrega: 5 días hábiles"
    )
    
    # Gestor de respuestas
    gestor = GestorRespuestas(bc)
    
    print("✅ Sistema inicializado correctamente\n")
    return bd, bc, gestor

def simular_conversacion(bd, gestor, telefono="test123"):
    """Simula una conversación completa"""
    print("=" * 60)
    print("🤖 SIMULADOR DE CONVERSACIÓN CON EL CHATBOT")
    print("=" * 60)
    print("Escribe 'salir' para terminar\n")
    
    # Crear o recuperar usuario
    usuario = bd.obtener_usuario(telefono)
    if not usuario:
        usuario = Usuario(telefono=telefono, nombre="Usuario de Prueba")
        bd.guardar_usuario(usuario)
        print(f"✅ Nuevo usuario creado: {usuario.telefono}\n")
    else:
        print(f"✅ Usuario existente: {usuario.nombre}\n")
    
    # Loop de conversación
    while True:
        # Input del usuario
        texto_usuario = input("👤 Tú: ")
        
        if texto_usuario.lower() == 'salir':
            print("\n👋 ¡Hasta luego!")
            break
        
        # Crear mensaje
        mensaje = Mensaje(
            telefono=telefono,
            contenido=texto_usuario,
            es_bot=False
        )
        
        # Guardar mensaje del usuario
        bd.guardar_mensaje(mensaje)
        
        # Generar respuesta
        respuesta = gestor.generar_respuesta(mensaje)
        
        # Guardar respuesta del bot
        mensaje_bot = Mensaje(
            telefono=telefono,
            contenido=respuesta,
            es_bot=True
        )
        bd.guardar_mensaje(mensaje_bot)
        
        # Mostrar respuesta
        print(f"\n🤖 Bot:\n{respuesta}\n")
        print("-" * 60 + "\n")

def menu_principal():
    """Menú principal del script de pruebas"""
    bd, bc, gestor = inicializar_sistema()
    
    while True:
        print("\n" + "=" * 60)
        print("MENÚ PRINCIPAL - CHATBOT UNIVERSITARIO")
        print("=" * 60)
        print("1. Simular conversación con el bot")
        print("2. Ver estadísticas")
        print("3. Probar procesador de lenguaje")
        print("4. Ver eventos próximos")
        print("5. Ver horarios disponibles")
        print("6. Ver carreras")
        print("7. Salir")
        print("=" * 60)
        
        opcion = input("\nElige una opción: ")
        
        if opcion == "1":
            simular_conversacion(bd, gestor)
            
        elif opcion == "2":
            stats = bd.obtener_estadisticas()
            print("\n📊 ESTADÍSTICAS:")
            print(f"Total usuarios: {stats['total_usuarios']}")
            print(f"Total mensajes: {stats['total_mensajes']}")
            print(f"Mensajes hoy: {stats['mensajes_hoy']}")
            print(f"Usuarios activos hoy: {stats['usuarios_activos_hoy']}")
            
        elif opcion == "3":
            procesador = ProcesadorLenguajeNatural()
            texto = input("\nEscribe un mensaje para analizar: ")
            mensaje = Mensaje(telefono="test", contenido=texto)
            tipo = procesador.clasificar_mensaje(mensaje)
            intenciones = procesador.extraer_intenciones(mensaje)
            
            print(f"\n📝 Análisis:")
            print(f"Tipo de mensaje: {tipo.value}")
            print(f"Servicio detectado: {intenciones.get('servicio', 'Ninguno')}")
            print(f"Carrera detectada: {intenciones.get('carrera', 'Ninguna')}")
            print(f"Es pregunta: {'Sí' if intenciones['es_pregunta'] else 'No'}")
            
        elif opcion == "4":
            eventos = bc.obtener_eventos_proximos(60)
            print(f"\n🎉 EVENTOS PRÓXIMOS ({len(eventos)}):\n")
            for evento in eventos:
                print(evento.obtener_info())
                
        elif opcion == "5":
            print("\n📅 HORARIOS DISPONIBLES:\n")
            for horario in bc.horarios.values():
                print(horario.obtener_info())
                
        elif opcion == "6":
            print("\n🎓 CARRERAS DISPONIBLES:\n")
            for carrera in bc.carreras.values():
                print(carrera.obtener_info())
                
        elif opcion == "7":
            print("\n👋 ¡Hasta luego!")
            break
            
        else:
            print("\n❌ Opción inválida")
        
        input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()