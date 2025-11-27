from datetime import datetime
from enum import Enum
from typing import Optional
import uuid

class TipoMensaje(Enum):
    
    CONSULTA_HORARIO = "consulta_horario"
    CONSULTA_EVENTO = "consulta_evento"
    CONSULTA_CARRERA = "consulta_carrera"
    CONSULTA_SERVICIO = "consulta_servicio"
    CONSULTA_TRAMITE = "consulta_tramite"
    SALUDO = "saludo"
    DESPEDIDA = "despedida"
    OTRO = "otro"

class Mensaje:
    
    
    def __init__(self, telefono: str, contenido: str, es_bot: bool = False):
        self.id = str(uuid.uuid4())
        self.telefono = telefono
        self.contenido = contenido
        self.es_bot = es_bot
        self.timestamp = datetime.now()
        self.tipo: Optional[TipoMensaje] = None
        self.procesado = False
        
    def clasificar(self, tipo: TipoMensaje):
      
        self.tipo = tipo
        
    def marcar_procesado(self):
        
        self.procesado = True
        
    def to_dict(self) -> dict:
      
        return {
            'id': self.id,
            'telefono': self.telefono,
            'contenido': self.contenido,
            'es_bot': self.es_bot,
            'timestamp': self.timestamp.isoformat(),
            'tipo': self.tipo.value if self.tipo else None,
            'procesado': self.procesado
        }
        
    @classmethod
    def from_dict(cls, data: dict):
        
        mensaje = cls(
            telefono=data['telefono'],
            contenido=data['contenido'],
            es_bot=data.get('es_bot', False)
        )
        mensaje.id = data['id']
        mensaje.timestamp = datetime.fromisoformat(data['timestamp'])
        if data.get('tipo'):
            mensaje.tipo = TipoMensaje(data['tipo'])
        mensaje.procesado = data.get('procesado', False)
        return mensaje
    
    def __str__(self) -> str:
        emisor = "Bot" if self.es_bot else "Usuario"
        return f"{emisor}: {self.contenido}"