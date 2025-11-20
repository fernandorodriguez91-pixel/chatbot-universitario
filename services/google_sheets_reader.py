from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os

class GoogleSheetsReader:
    def __init__(self, credentials_file, sheet_id):
        """
        Inicializa el lector de Google Sheets
        
        Args:
            credentials_file: Ruta al archivo credentials.json
            sheet_id: ID del Google Sheet
        """
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        self.credentials_file = credentials_file
        self.sheet_id = sheet_id
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Autentica con Google Sheets API"""
        try:
            credentials = Credentials.from_service_account_file(
                self.credentials_file, 
                scopes=self.SCOPES
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            print("✅ Autenticación con Google Sheets exitosa")
        except Exception as e:
            print(f"❌ Error en autenticación: {e}")
            raise
    
    def read_range(self, sheet_name, range_notation='A:Z'):
        """
        Lee un rango de datos de una hoja específica
        
        Args:
            sheet_name: Nombre de la hoja (ej: "Horarios", "Eventos")
            range_notation: Rango a leer (ej: "A:Z", "A1:D100")
        
        Returns:
            Lista de diccionarios con los datos
        """
        try:
            range_name = f"'{sheet_name}'!{range_notation}"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                print(f"⚠️  No hay datos en {sheet_name}")
                return []
            
            # Primera fila son los headers
            headers = values[0]
            data = []
            
            # Convertir filas a diccionarios
            for row in values[1:]:
                # Rellenar celdas vacías
                while len(row) < len(headers):
                    row.append('')
                
                row_dict = {headers[i]: row[i] for i in range(len(headers))}
                data.append(row_dict)
            
            print(f"✅ Leídos {len(data)} registros de {sheet_name}")
            return data
        
        except Exception as e:
            print(f"❌ Error leyendo {sheet_name}: {e}")
            return []
    
    def get_horarios(self):
        """Obtiene todos los horarios"""
        return self.read_range('Horarios')
    
    def get_eventos(self):
        """Obtiene todos los eventos"""
        return self.read_range('Eventos')
    
    def get_carreras(self):
        """Obtiene todas las carreras"""
        return self.read_range('Carreras')
    
    def get_avisos(self):
        """Obtiene todos los avisos"""
        return self.read_range('Avisos')
    
    def get_all_data(self):
        """Obtiene todos los datos (horarios, eventos, carreras, avisos)"""
        return {
            'horarios': self.get_horarios(),
            'eventos': self.get_eventos(),
            'carreras': self.get_carreras(),
            'avisos': self.get_avisos()
        }


# Uso de ejemplo:
if __name__ == "__main__":
    # Configuración
    CREDENTIALS_FILE = "api/credentials.json"  # Ruta a tu archivo de credenciales
    SHEET_ID = "1nEuZLDuowW5d9Li-91fO3DObAXTsuPYtTZM5vGpn_qo"
    
    # Crear lector
    reader = GoogleSheetsReader(CREDENTIALS_FILE, SHEET_ID)
    
    # Obtener datos
    print("\n" + "="*60)
    print("HORARIOS")
    print("="*60)
    horarios = reader.get_horarios()
    for h in horarios[:3]:  # Mostrar primeros 3
        print(h)
    
    print("\n" + "="*60)
    print("EVENTOS")
    print("="*60)
    eventos = reader.get_eventos()
    for e in eventos[:3]:  # Mostrar primeros 3
        print(e)
    
    print("\n" + "="*60)
    print("CARRERAS")
    print("="*60)
    carreras = reader.get_carreras()
    for c in carreras[:3]:  # Mostrar primeros 3
        print(c)