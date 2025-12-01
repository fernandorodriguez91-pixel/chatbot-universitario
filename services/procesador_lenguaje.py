from typing import Optional, List, Tuple
import re
from models.mensaje import Mensaje, TipoMensaje

class ProcesadorLenguajeNatural:
    
    def __init__(self):
        self.palabras_horario = [
            'horario', 'abierto', 'cierra', 'abre', 'hora', 'cuando',
            'biblioteca', 'laboratorio', 'comedor', 'cafetería'
        ]
        
        self.palabras_evento = [
            'evento', 'actividad', 'cuando', 'fecha', 'examen',
            'inscripciones', 'calendario', 'periodo', 'vacaciones'
        ]
        
        self.palabras_carrera = [
            'carrera', 'licenciatura', 'ingenieria', 'ingeniería',
            'programa', 'estudiar', 'materias', 'plan de estudios', 
            'semestre', 'mecatronica', 'mecatonica', 'ingenieria mecatronica'
        ]       
        
        self.palabras_tramite = [
            'trámite', 'documentos', 'credencial', 'constancia',
            'certificado', 'título', 'como solicitar', 'requisitos'
        ]
        
        self.palabras_servicio = [
            'servicio', 'servicios', 'disponible', 'que hay',
            'ofrecen', 'oferta', 'recursos', 'instalaciones'
        ]
        
        self.palabras_suspension = [
            'suspensión', 'suspensiones', 'clases', 'hay clases', 'cancelado',
            'canceladas', 'suspendido', 'actividades', 'hoy', 'suspension'
        ]
        
        self.saludos = [
            'hola', 'buenos dias', 'buenas tardes', 'buenas noches',
            'que tal', 'saludos', 'hey', 'ola'
        ]
        
        self.despedidas = [
            'adios', 'hasta luego', 'chao', 'bye', 'nos vemos',
            'gracias', 'ok', 'perfecto'
        ]
        
    def limpiar_texto(self, texto: str) -> str:
        texto = texto.lower()
        texto = texto.replace('á', 'a').replace('é', 'e').replace('í', 'i')
        texto = texto.replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
        texto = re.sub(r'[^a-z0-9\s]', '', texto)
        return texto.strip()
    
    def clasificar_mensaje(self, mensaje: Mensaje) -> TipoMensaje:
        texto_limpio = self.limpiar_texto(mensaje.contenido)
        palabras = texto_limpio.split()
        
        if any(saludo in texto_limpio for saludo in self.saludos):
            return TipoMensaje.SALUDO
        
        if any(despedida in texto_limpio for despedida in self.despedidas):
            return TipoMensaje.DESPEDIDA
        
        score_horario = sum(1 for palabra in self.palabras_horario if palabra in texto_limpio)
        score_evento = sum(1 for palabra in self.palabras_evento if palabra in texto_limpio)
        score_carrera = sum(1 for palabra in self.palabras_carrera if palabra in texto_limpio)
        score_tramite = sum(1 for palabra in self.palabras_tramite if palabra in texto_limpio)
        score_servicio = sum(1 for palabra in self.palabras_servicio if palabra in texto_limpio)
        score_suspension = sum(1 for palabra in self.palabras_suspension if palabra in texto_limpio)
        
        scores = {
            TipoMensaje.CONSULTA_HORARIO: score_horario,
            TipoMensaje.CONSULTA_EVENTO: score_evento,
            TipoMensaje.CONSULTA_CARRERA: score_carrera,
            TipoMensaje.CONSULTA_TRAMITE: score_tramite,
            TipoMensaje.CONSULTA_SERVICIO: score_servicio,
            TipoMensaje.CONSULTA_SUSPENSION: score_suspension
        }
        
        max_score = max(scores.values())
        if max_score > 0:
            return max(scores, key=scores.get)
        
        return TipoMensaje.OTRO
    
    def extraer_servicio(self, texto: str) -> Optional[str]:
        texto_limpio = self.limpiar_texto(texto)
        
        servicios = {
            'biblioteca': ['biblioteca', 'libros', 'biblio'],
            'laboratorio': ['laboratorio', 'lab', 'laboratorios', 'labs'],
            'comedor': ['comedor', 'cafeteria', 'cafe', 'comida']
        }
        
        for servicio, keywords in servicios.items():
            if any(keyword in texto_limpio for keyword in keywords):
                return servicio
        
        return None
    
    def extraer_carrera(self, texto: str) -> Optional[str]:
        texto_limpio = self.limpiar_texto(texto)
        
        carreras = {
            'sistemas': ['sistemas', 'computacion', 'software', 'informatica'],
            'industrial': ['industrial', 'produccion'],
            'civil': ['civil', 'construccion'],
            'ingenieria mecatronica': [
            'ingenieria mecatronica',
            'mecanica',
            'mecatronica',
            'ingeneria' 
        ],
            'administracion': ['administracion', 'negocios', 'empresas'],
            'contabilidad': ['contabilidad', 'contador']
        }
        
        for carrera, keywords in carreras.items():
            if any(keyword in texto_limpio for keyword in keywords):
                return carrera
        
        return None
    
    def es_pregunta(self, texto: str) -> bool:
        palabras_pregunta = ['que', 'como', 'cuando', 'donde', 'quien', 
                            'por que', 'cual', 'cuales', 'cuanto']
        texto_limpio = texto.lower()
        return any(palabra in texto_limpio for palabra in palabras_pregunta) or texto.strip().endswith('?')
    
    def extraer_intenciones(self, mensaje: Mensaje) -> dict:
        tipo = self.clasificar_mensaje(mensaje)
        
        intenciones = {
            'tipo': tipo,
            'servicio': self.extraer_servicio(mensaje.contenido),
            'carrera': self.extraer_carrera(mensaje.contenido),
            'es_pregunta': self.es_pregunta(mensaje.contenido),
            'texto_original': mensaje.contenido,
            'texto_limpio': self.limpiar_texto(mensaje.contenido)
        }
        
        return intenciones