from enum import Enum
from datetime import datetime
import pytz

class TipoMensaje(Enum):
    SALUDO = "saludo"
    DESPEDIDA = "despedida"
    CONSULTA_HORARIO = "consulta_horario"
    CONSULTA_EVENTO = "consulta_evento"
    CONSULTA_CARRERA = "consulta_carrera"
    CONSULTA_TRAMITE = "consulta_tramite"
    CONSULTA_SERVICIO = "consulta_servicio"
    CONSULTA_SUSPENSION = "consulta_suspension"
    OTRO = "otro"

class Mensaje:
    def __init__(self, telefono: str, contenido: str, es_bot: bool = False):
        self.telefono = telefono
        self.contenido = contenido
        self.es_bot = es_bot
        self.timestamp = self._obtener_timestamp()
        self.tipo = self._clasificar_tipo()
    
    def _obtener_timestamp(self) -> datetime:
        tz_mexico = pytz.timezone('America/Tijuana')
        return datetime.now(tz_mexico)
    
    def _clasificar_tipo(self) -> TipoMensaje:
        if self.contenido.lower().startswith('!'):
            return TipoMensaje.OTRO
        return TipoMensaje.OTRO
    
    def to_dict(self) -> dict:
        return {
            'telefono': self.telefono,
            'contenido': self.contenido,
            'es_bot': self.es_bot,
            'timestamp': self.timestamp.isoformat(),
            'tipo': self.tipo.value if self.tipo else None
        }