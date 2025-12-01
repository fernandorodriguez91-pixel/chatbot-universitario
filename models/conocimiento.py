from datetime import datetime, time
from typing import List, Dict, Optional
from enum import Enum

class DiaSemana(Enum):
    
    LUNES = "lunes"
    MARTES = "martes"
    MIERCOLES = "miércoles"
    JUEVES = "jueves"
    VIERNES = "viernes"
    SABADO = "sábado"
    DOMINGO = "domingo"

class Horario:
    
    def __init__(self, servicio: str, dias: List[DiaSemana], 
                 hora_inicio: time, hora_fin: time, notas: str = ""):
        self.servicio = servicio
        self.dias = dias
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.notas = notas
        
    def esta_abierto(self, dia: DiaSemana, hora: time) -> bool:
     
        if dia not in self.dias:
            return False
        return self.hora_inicio <= hora <= self.hora_fin
    
    def obtener_info(self) -> str:
     
        dias_str = ", ".join([d.value.capitalize() for d in self.dias])
        info = f"📅 *{self.servicio}*\n"
        info += f"🕐 {dias_str}\n"
        info += f"⏰ {self.hora_inicio.strftime('%H:%M')} - {self.hora_fin.strftime('%H:%M')}\n"
        if self.notas:
            info += f"ℹ️ {self.notas}\n"
        return info

class Evento:

    
    def __init__(self, nombre: str, descripcion: str, 
                 fecha_inicio: datetime, fecha_fin: Optional[datetime] = None,
                 lugar: str = "", categoria: str = "General"):
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin or fecha_inicio
        self.lugar = lugar
        self.categoria = categoria
        
    def esta_activo(self, fecha: datetime = None) -> bool:
        
        if fecha is None:
            fecha = datetime.now()
        return self.fecha_inicio <= fecha <= self.fecha_fin
    
    def dias_para_evento(self) -> int:
       
        delta = self.fecha_inicio - datetime.now()
        return delta.days
    
    def obtener_info(self) -> str:
        
        info = f"🎓 *{self.nombre}*\n"
        info += f"📝 {self.descripcion}\n"
        
        if self.fecha_inicio.date() == self.fecha_fin.date():
            info += f"📅 {self.fecha_inicio.strftime('%d/%m/%Y')}\n"
        else:
            info += f"📅 Del {self.fecha_inicio.strftime('%d/%m/%Y')} al {self.fecha_fin.strftime('%d/%m/%Y')}\n"
        
        if self.lugar:
            info += f"📍 {self.lugar}\n"
            
        dias = self.dias_para_evento()
        if dias > 0:
            info += f"⏳ Faltan {dias} días\n"
        elif dias == 0:
            info += f"🔔 ¡Es hoy!\n"
        else:
            info += f"✅ Evento pasado\n"
            
        return info

class Carrera:
  
    
    def __init__(self, nombre: str, duracion_semestres: int, 
                 descripcion: str, coordinador: str = ""):
        self.nombre = nombre
        self.duracion_semestres = duracion_semestres
        self.descripcion = descripcion
        self.coordinador = coordinador
        self.materias: Dict[int, List[str]] = {}
        
    def agregar_materias(self, semestre: int, materias: List[str]):
    
        self.materias[semestre] = materias
        
    def obtener_info(self) -> str:
  
        respuesta = ""
    
        respuesta += f"🎓 *{self.nombre.upper()}*\n"
        respuesta += "="*50 + "\n\n"
    
        if self.descripcion and str(self.descripcion).strip():
            respuesta += f"📚 *DESCRIPCIÓN:*\n"
            respuesta += f"{self.descripcion}\n\n"
    
        respuesta += f"⏱️ *DURACIÓN:*\n"
        respuesta += f"{self.duracion_semestres} semestres\n\n"
    
        if self.coordinador and str(self.coordinador).strip():
            respuesta += f"👤 *COORDINADOR:*\n"
            respuesta += f"{self.coordinador}\n\n"
    
        respuesta += "="*50 + "\n"
        respuesta += "¿Necesitas más información? 😊"
    
        return respuesta
    
class Servicio:
    def __init__(self, nombre: str, descripcion: str = "", pagos: str = "", dias: str = "", lugar: str = ""):
        self.nombre = nombre
        self.descripcion = descripcion
        self.pagos = pagos
        self.dias = dias
        self.lugar = lugar
    
    def obtener_info(self) -> str:
        respuesta = f"📋 *{self.nombre.upper()}*\n"
        respuesta += "="*50 + "\n\n"
        
        if self.descripcion and self.descripcion.strip():
            respuesta += f"{self.descripcion}\n\n"
        
        if self.pagos and self.pagos.strip():
            respuesta += f"💳 *Pagos:* {self.pagos}\n"
        
        if self.dias and self.dias.strip():
            respuesta += f"📅 *Días:* {self.dias}\n"
        
        if self.lugar and self.lugar.strip():
            respuesta += f"📍 *Lugar:* {self.lugar}\n"
        
        if not any([self.pagos, self.dias, self.lugar]):
            respuesta += "ℹ️ Sin información adicional disponible\n"
        
        respuesta += "\n" + "="*50
        respuesta += "\n¿Necesitas más información? 😊"
        
        return respuesta

class Suspension:
    def __init__(self, fecha: str, suspension: str):
        self.fecha = fecha
        self.suspension = suspension
    
    def obtener_info(self) -> str:
        return f"📅 {self.fecha}\n{self.suspension}"

class BaseConocimiento:

    
    def __init__(self):
        self.horarios: Dict[str, Horario] = {}
        self.eventos: List[Evento] = []
        self.carreras: Dict[str, Carrera] = {}
        self.tramites: Dict[str, str] = {}
        self.servicios = {}
        self.suspensiones: List[Suspension] = []
        
    def agregar_horario(self, horario: Horario):
       
        self.horarios[horario.servicio.lower()] = horario
        
    def agregar_evento(self, evento: Evento):
   
        self.eventos.append(evento)
        
    def agregar_carrera(self, carrera: Carrera):
       
        self.carreras[carrera.nombre.lower()] = carrera
        
    def agregar_tramite(self, nombre: str, descripcion: str):
        
        self.tramites[nombre.lower()] = descripcion

    def agregar_servicio(self, servicio: Servicio):
        
        self.servicios[servicio.nombre.lower()] = servicio
    
    def agregar_suspension(self, suspension: Suspension):
        self.suspensiones.append(suspension)
        
    def buscar_horario(self, servicio: str) -> Optional[Horario]:
       
        return self.horarios.get(servicio.lower())
    
    def obtener_eventos_proximos(self, dias: int = 30) -> List[Evento]:
        
        eventos_proximos = []
        for evento in self.eventos:
            dias_faltantes = evento.dias_para_evento()
            if 0 <= dias_faltantes <= dias:
                eventos_proximos.append(evento)
        return sorted(eventos_proximos, key=lambda e: e.fecha_inicio)
    
    def buscar_carrera(self, nombre: str) -> Optional[Carrera]:
        
        return self.carreras.get(nombre.lower())
    
    def buscar_tramite(self, nombre: str) -> Optional[str]:
        
        return self.tramites.get(nombre.lower())
    
    def buscar_servicio(self, nombre: str) -> Optional[Servicio]:
        return self.servicios.get(nombre.lower())

    def obtener_suspension(self, fecha: datetime = None) -> Optional[str]:
        from datetime import datetime, timedelta
    
        if fecha is None:
            fecha = datetime.now()
    
        dia = fecha.day
    
        meses = {
            1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
            5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
            9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
        }
    
        mes = meses[fecha.month]
        fecha_buscada = f"{dia} de {mes}".lower()
    
        for susp in self.suspensiones:
            fecha_suspension = susp.fecha.lower().strip()
            if fecha_suspension == fecha_buscada:
                return susp.suspension
    
        return None

    def obtener_suspension_hoy(self) -> Optional[str]:
        from datetime import datetime
        return self.obtener_suspension(datetime.now())

    def obtener_suspension_manana(self) -> Optional[str]:
        from datetime import datetime, timedelta
        manana = datetime.now() + timedelta(days=1)
        return self.obtener_suspension(manana)

    def obtener_suspension_fecha_relativa(self, texto: str) -> Optional[str]:
        from datetime import datetime, timedelta
    
        texto_limpio = texto.lower()
    
        if 'hoy' in texto_limpio:
            return self.obtener_suspension(datetime.now())
    
        elif 'mañana' in texto_limpio or 'manana' in texto_limpio:
            return self.obtener_suspension(datetime.now() + timedelta(days=1))
    
        elif 'pasado mañana' in texto_limpio or 'pasado manana' in texto_limpio:
            return self.obtener_suspension(datetime.now() + timedelta(days=2))
    
        elif 'próximo lunes' in texto_limpio or 'proximo lunes' in texto_limpio:
            hoy = datetime.now()
            dias_hasta_lunes = (7 - hoy.weekday()) % 7
            if dias_hasta_lunes == 0:
                dias_hasta_lunes = 7
            return self.obtener_suspension(hoy + timedelta(days=dias_hasta_lunes))
    
        elif 'próximo martes' in texto_limpio or 'proximo martes' in texto_limpio:
            hoy = datetime.now()
            dias_hasta_martes = (8 - hoy.weekday()) % 7
            if dias_hasta_martes == 0:
                dias_hasta_martes = 7
            return self.obtener_suspension(hoy + timedelta(days=dias_hasta_martes))
    
        elif 'próximo miércoles' in texto_limpio or 'proximo miercoles' in texto_limpio or 'proximo miercoles' in texto_limpio:
            hoy = datetime.now()
            dias_hasta_miercoles = (9 - hoy.weekday()) % 7
            if dias_hasta_miercoles == 0:
                dias_hasta_miercoles = 7
            return self.obtener_suspension(hoy + timedelta(days=dias_hasta_miercoles))
    
        elif 'próximo jueves' in texto_limpio or 'proximo jueves' in texto_limpio:
            hoy = datetime.now()
            dias_hasta_jueves = (10 - hoy.weekday()) % 7
            if dias_hasta_jueves == 0:
                dias_hasta_jueves = 7
            return self.obtener_suspension(hoy + timedelta(days=dias_hasta_jueves))
    
        elif 'próximo viernes' in texto_limpio or 'proximo viernes' in texto_limpio:
            hoy = datetime.now()
            dias_hasta_viernes = (11 - hoy.weekday()) % 7
            if dias_hasta_viernes == 0:
                dias_hasta_viernes = 7
            return self.obtener_suspension(hoy + timedelta(days=dias_hasta_viernes))
    
        else:
            return None