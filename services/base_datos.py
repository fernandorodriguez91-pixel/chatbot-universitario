import json
import os
from typing import Optional, List, Dict
from datetime import datetime
from models.usuario import Usuario
from models.mensaje import Mensaje

class BaseDatos:
    """Clase para gestionar la persistencia de datos"""
    
    def __init__(self, ruta_datos: str = "datos"):
        self.ruta_datos = ruta_datos
        self.ruta_usuarios = os.path.join(ruta_datos, "usuarios.json")
        self.ruta_mensajes = os.path.join(ruta_datos, "mensajes.json")
        self._crear_directorio()
        self._inicializar_archivos()
        
    def _crear_directorio(self):
        """Crea el directorio de datos si no existe"""
        if not os.path.exists(self.ruta_datos):
            os.makedirs(self.ruta_datos)
    
    def _inicializar_archivos(self):
        """Inicializa los archivos JSON si no existen"""
        if not os.path.exists(self.ruta_usuarios):
            self._guardar_json(self.ruta_usuarios, {})
        if not os.path.exists(self.ruta_mensajes):
            self._guardar_json(self.ruta_mensajes, [])
    
    def _guardar_json(self, ruta: str, datos):
        """Guarda datos en formato JSON"""
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    
    def _cargar_json(self, ruta: str):
        """Carga datos desde un archivo JSON"""
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    # MÉTODOS PARA USUARIOS
    def guardar_usuario(self, usuario: Usuario) -> bool:
        """Guarda o actualiza un usuario"""
        try:
            usuarios = self._cargar_json(self.ruta_usuarios) or {}
            usuarios[usuario.telefono] = usuario.to_dict()
            self._guardar_json(self.ruta_usuarios, usuarios)
            return True
        except Exception as e:
            print(f"Error al guardar usuario: {e}")
            return False
    
    def obtener_usuario(self, telefono: str) -> Optional[Usuario]:
        """Obtiene un usuario por su teléfono"""
        usuarios = self._cargar_json(self.ruta_usuarios) or {}
        if telefono in usuarios:
            return Usuario.from_dict(usuarios[telefono])
        return None
    
    def usuario_existe(self, telefono: str) -> bool:
        """Verifica si un usuario existe"""
        usuarios = self._cargar_json(self.ruta_usuarios) or {}
        return telefono in usuarios
    
    def obtener_todos_usuarios(self) -> List[Usuario]:
        """Obtiene todos los usuarios"""
        usuarios = self._cargar_json(self.ruta_usuarios) or {}
        return [Usuario.from_dict(data) for data in usuarios.values()]
    
    # MÉTODOS PARA MENSAJES
    def guardar_mensaje(self, mensaje: Mensaje) -> bool:
        """Guarda un mensaje en el historial"""
        try:
            mensajes = self._cargar_json(self.ruta_mensajes) or []
            mensajes.append(mensaje.to_dict())
            self._guardar_json(self.ruta_mensajes, mensajes)
            return True
        except Exception as e:
            print(f"Error al guardar mensaje: {e}")
            return False
    
    def obtener_mensajes_usuario(self, telefono: str, limite: int = 50) -> List[Mensaje]:
        """Obtiene los últimos mensajes de un usuario"""
        mensajes = self._cargar_json(self.ruta_mensajes) or []
        mensajes_usuario = [
            Mensaje.from_dict(m) for m in mensajes 
            if m['telefono'] == telefono
        ]
        return mensajes_usuario[-limite:]
    
    def obtener_historial_completo(self, telefono: str) -> List[Mensaje]:
        """Obtiene el historial completo de un usuario"""
        mensajes = self._cargar_json(self.ruta_mensajes) or []
        return [Mensaje.from_dict(m) for m in mensajes if m['telefono'] == telefono]
    
    def contar_mensajes_usuario(self, telefono: str) -> int:
        """Cuenta los mensajes de un usuario"""
        mensajes = self._cargar_json(self.ruta_mensajes) or []
        return sum(1 for m in mensajes if m['telefono'] == telefono)
    
    # MÉTODOS DE ESTADÍSTICAS
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas generales del chatbot"""
        usuarios = self._cargar_json(self.ruta_usuarios) or {}
        mensajes = self._cargar_json(self.ruta_mensajes) or []
        
        return {
            'total_usuarios': len(usuarios),
            'total_mensajes': len(mensajes),
            'mensajes_hoy': self._contar_mensajes_hoy(mensajes),
            'usuarios_activos_hoy': self._contar_usuarios_activos_hoy(mensajes)
        }
    
    def _contar_mensajes_hoy(self, mensajes: List[dict]) -> int:
        """Cuenta mensajes de hoy"""
        hoy = datetime.now().date()
        return sum(
            1 for m in mensajes 
            if datetime.fromisoformat(m['timestamp']).date() == hoy
        )
    
    def _contar_usuarios_activos_hoy(self, mensajes: List[dict]) -> int:
        """Cuenta usuarios únicos que enviaron mensajes hoy"""
        hoy = datetime.now().date()
        usuarios_hoy = set()
        for m in mensajes:
            if datetime.fromisoformat(m['timestamp']).date() == hoy:
                usuarios_hoy.add(m['telefono'])
        return len(usuarios_hoy)
    
    def limpiar_mensajes_antiguos(self, dias: int = 90) -> int:
        """Elimina mensajes más antiguos que X días"""
        mensajes = self._cargar_json(self.ruta_mensajes) or []
        fecha_limite = datetime.now().timestamp() - (dias * 24 * 60 * 60)
        
        mensajes_filtrados = [
            m for m in mensajes
            if datetime.fromisoformat(m['timestamp']).timestamp() > fecha_limite
        ]
        
        eliminados = len(mensajes) - len(mensajes_filtrados)
        self._guardar_json(self.ruta_mensajes, mensajes_filtrados)
        return eliminados