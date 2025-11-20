from datetime import datetime
from typing import Optional
import json

class Usuario:
    """Clase para representar un usuario del chatbot"""
    
    def __init__(self, telefono: str, nombre: Optional[str] = None, 
                 carrera: Optional[str] = None, semestre: Optional[int] = None):
        self.telefono = telefono
        self.nombre = nombre
        self.carrera = carrera
        self.semestre = semestre
        self.fecha_registro = datetime.now()
        self.ultima_interaccion = datetime.now()
        self.conversaciones = []
        
    def actualizar_interaccion(self):
        """Actualiza la fecha de última interacción"""
        self.ultima_interaccion = datetime.now()
        
    def actualizar_perfil(self, nombre: str = None, carrera: str = None, semestre: int = None):
        """Actualiza información del perfil del usuario"""
        if nombre:
            self.nombre = nombre
        if carrera:
            self.carrera = carrera
        if semestre:
            self.semestre = semestre
            
    def agregar_conversacion(self, conversacion_id: str):
        """Agrega una conversación al historial"""
        self.conversaciones.append(conversacion_id)
        
    def to_dict(self) -> dict:
        """Convierte el objeto a diccionario"""
        return {
            'telefono': self.telefono,
            'nombre': self.nombre,
            'carrera': self.carrera,
            'semestre': self.semestre,
            'fecha_registro': self.fecha_registro.isoformat(),
            'ultima_interaccion': self.ultima_interaccion.isoformat(),
            'conversaciones': self.conversaciones
        }
        
    @classmethod
    def from_dict(cls, data: dict):
        """Crea un objeto Usuario desde un diccionario"""
        usuario = cls(
            telefono=data['telefono'],
            nombre=data.get('nombre'),
            carrera=data.get('carrera'),
            semestre=data.get('semestre')
        )
        if 'fecha_registro' in data:
            usuario.fecha_registro = datetime.fromisoformat(data['fecha_registro'])
        if 'ultima_interaccion' in data:
            usuario.ultima_interaccion = datetime.fromisoformat(data['ultima_interaccion'])
        if 'conversaciones' in data:
            usuario.conversaciones = data['conversaciones']
        return usuario
    
    def __str__(self) -> str:
        return f"Usuario({self.telefono}, {self.nombre}, {self.carrera})"