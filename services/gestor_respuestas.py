from typing import Optional
from datetime import datetime
from models.mensaje import Mensaje, TipoMensaje
from models.conocimiento import BaseConocimiento, DiaSemana
from services.procesador_lenguaje import ProcesadorLenguajeNatural

class GestorRespuestas:
    """Clase que gestiona las respuestas del chatbot"""
    
    def __init__(self, base_conocimiento: BaseConocimiento):
        self.base_conocimiento = base_conocimiento
        self.procesador = ProcesadorLenguajeNatural()
        
    def generar_respuesta(self, mensaje: Mensaje) -> str:
        """Genera una respuesta basada en el mensaje recibido"""
        # Extraer intenciones del mensaje
        intenciones = self.procesador.extraer_intenciones(mensaje)
        tipo = intenciones['tipo']
        
        # Generar respuesta según el tipo
        if tipo == TipoMensaje.SALUDO:
            return self._respuesta_saludo()
        
        elif tipo == TipoMensaje.DESPEDIDA:
            return self._respuesta_despedida()
        
        elif tipo == TipoMensaje.CONSULTA_HORARIO:
            servicio = intenciones.get('servicio')
            return self._respuesta_horario(servicio)
        
        elif tipo == TipoMensaje.CONSULTA_EVENTO:
            return self._respuesta_eventos()
        
        elif tipo == TipoMensaje.CONSULTA_CARRERA:
            carrera = intenciones.get('carrera')
            return self._respuesta_carrera(carrera)
        
        elif tipo == TipoMensaje.CONSULTA_TRAMITE:
            return self._respuesta_tramites()
        
        else:
            return self._respuesta_default()
    
    def _respuesta_saludo(self) -> str:
        """Genera respuesta de saludo"""
        hora = datetime.now().hour
        if 5 <= hora < 12:
            saludo = "¡Buenos días! 🌅"
        elif 12 <= hora < 19:
            saludo = "¡Buenas tardes! ☀️"
        else:
            saludo = "¡Buenas noches! 🌙"
        
        respuesta = f"{saludo}\n\n"
        respuesta += "Soy tu asistente virtual universitario. 🎓\n\n"
        respuesta += "Puedo ayudarte con:\n"
        respuesta += "📚 Horarios de biblioteca, laboratorios y comedor\n"
        respuesta += "🎉 Eventos del ciclo escolar\n"
        respuesta += "🎓 Información sobre carreras\n"
        respuesta += "📋 Trámites administrativos\n\n"
        respuesta += "¿En qué puedo ayudarte hoy?"
        
        return respuesta
    
    def _respuesta_despedida(self) -> str:
        """Genera respuesta de despedida"""
        respuestas = [
            "¡Hasta pronto! 👋 Estoy aquí cuando me necesites.",
            "¡Adiós! 😊 Que tengas un excelente día.",
            "¡Nos vemos! 🎓 Mucho éxito en tus estudios."
        ]
        import random
        return random.choice(respuestas)
    
    def _respuesta_horario(self, servicio: Optional[str]) -> str:
        """Genera respuesta sobre horarios"""
        if servicio is None:
            # Mostrar todos los horarios
            respuesta = "📅 *HORARIOS DE SERVICIOS*\n\n"
            if not self.base_conocimiento.horarios:
                return "Lo siento, no tengo información de horarios disponible. 😔"
            
            for horario in self.base_conocimiento.horarios.values():
                respuesta += horario.obtener_info() + "\n"
            return respuesta
        
        # Buscar horario específico
        horario = self.base_conocimiento.buscar_horario(servicio)
        if horario:
            return horario.obtener_info()
        else:
            respuesta = f"Lo siento, no encontré información sobre '{servicio}'. 😔\n\n"
            respuesta += "Servicios disponibles:\n"
            for nombre in self.base_conocimiento.horarios.keys():
                respuesta += f"• {nombre.capitalize()}\n"
            return respuesta
    
    def _respuesta_eventos(self) -> str:
        """Genera respuesta sobre eventos"""
        eventos_proximos = self.base_conocimiento.obtener_eventos_proximos(dias=60)
        
        if not eventos_proximos:
            return "No hay eventos próximos registrados en este momento. 📅"
        
        respuesta = "🎉 *PRÓXIMOS EVENTOS*\n\n"
        for evento in eventos_proximos[:5]:  # Mostrar máximo 5 eventos
            respuesta += evento.obtener_info() + "\n"
        
        if len(eventos_proximos) > 5:
            respuesta += f"\n_Y {len(eventos_proximos) - 5} eventos más..._"
        
        return respuesta
    
    def _respuesta_carrera(self, carrera: Optional[str]) -> str:
        """Genera respuesta sobre carreras"""
        if carrera is None:
            # Mostrar lista de carreras
            if not self.base_conocimiento.carreras:
                return "Lo siento, no tengo información de carreras disponible. 😔"
            
            respuesta = "🎓 *CARRERAS DISPONIBLES*\n\n"
            for nombre in self.base_conocimiento.carreras.keys():
                respuesta += f"• {nombre.capitalize()}\n"
            respuesta += "\n¿Sobre cuál te gustaría saber más?"
            return respuesta
        
        # Buscar carrera específica
        info_carrera = self.base_conocimiento.buscar_carrera(carrera)
        if info_carrera:
            return info_carrera.obtener_info()
        else:
            respuesta = f"No encontré información sobre la carrera '{carrera}'. 😔\n\n"
            respuesta += "Carreras disponibles:\n"
            for nombre in self.base_conocimiento.carreras.keys():
                respuesta += f"• {nombre.capitalize()}\n"
            return respuesta
    
    def _respuesta_tramites(self) -> str:
        """Genera respuesta sobre trámites"""
        if not self.base_conocimiento.tramites:
            return "Lo siento, no tengo información de trámites disponible. 😔"
        
        respuesta = "📋 *TRÁMITES DISPONIBLES*\n\n"
        for nombre, descripcion in self.base_conocimiento.tramites.items():
            respuesta += f"*{nombre.upper()}*\n"
            respuesta += f"{descripcion}\n\n"
        
        return respuesta
    
    def _respuesta_default(self) -> str:
        """Respuesta por defecto cuando no se entiende el mensaje"""
        respuesta = "Lo siento, no entendí tu pregunta. 🤔\n\n"
        respuesta += "Puedo ayudarte con:\n"
        respuesta += "📚 Horarios (biblioteca, laboratorios, comedor)\n"
        respuesta += "🎉 Eventos del ciclo escolar\n"
        respuesta += "🎓 Información sobre carreras\n"
        respuesta += "📋 Trámites administrativos\n\n"
        respuesta += "¿Podrías reformular tu pregunta?"
        
        return respuesta
    
    def obtener_dia_actual(self) -> DiaSemana:
        """Obtiene el día actual de la semana"""
        dias = {
            0: DiaSemana.LUNES,
            1: DiaSemana.MARTES,
            2: DiaSemana.MIERCOLES,
            3: DiaSemana.JUEVES,
            4: DiaSemana.VIERNES,
            5: DiaSemana.SABADO,
            6: DiaSemana.DOMINGO
        }
        return dias[datetime.now().weekday()]