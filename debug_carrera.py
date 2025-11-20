#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')

print("="*70)
print("🔍 SCRIPT DE DEBUG - CARRERA")
print("="*70)

# Test 1: Importar módulos
print("\n1️⃣ Importando módulos...")
try:
    from services.google_sheets_reader import GoogleSheetsReader
    from models.conocimiento import Carrera, BaseConocimiento
    from services.gestor_respuestas import GestorRespuestas
    print("   ✅ Módulos importados correctamente")
except Exception as e:
    print(f"   ❌ Error importando: {e}")
    sys.exit(1)

# Test 2: Leer Google Sheets
print("\n2️⃣ Leyendo Google Sheets...")
try:
    CREDENTIALS_FILE = "api/credentials.json"
    SHEET_ID = "1nEuZLDuowW5d9Li-91fO3DObAXTsuPYtTZM5vGpn_qo"
    
    reader = GoogleSheetsReader(CREDENTIALS_FILE, SHEET_ID)
    carreras_data = reader.get_carreras()
    
    print(f"   ✅ Google Sheets leído correctamente")
    print(f"   📊 Total de carreras: {len(carreras_data)}")
    
    if carreras_data:
        print(f"\n   📋 PRIMERAS CARRERA:")
        print(f"   {carreras_data[0]}")
    
except Exception as e:
    print(f"   ❌ Error leyendo Sheets: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Verificar estructura de datos
print("\n3️⃣ Verificando estructura de datos...")
if carreras_data and len(carreras_data) > 0:
    c = carreras_data[0]
    print(f"\n   Claves en cada carrera:")
    for key in c.keys():
        print(f"      • {key}: {repr(c[key])}")
else:
    print("   ⚠️ No hay datos de carreras")

# Test 4: Crear objeto Carrera
print("\n4️⃣ Creando objeto Carrera...")
try:
    if carreras_data and len(carreras_data) > 0:
        c = carreras_data[0]
        
        # Ver exactamente qué valores se usan
        duracion = c.get('Duracion_Semestres', 8)
        print(f"   Duración recibida: {repr(duracion)}")
        
        if isinstance(duracion, str):
            duracion = int(duracion)
        
        carrera = Carrera(
            nombre=str(c.get('Nombre', 'Carrera')),
            duracion_semestres=duracion,
            descripcion=str(c.get('Descripción', '')),
            coordinador=str(c.get('Coordinador', ''))
        )
        
        print(f"   ✅ Carrera creada: {carrera.nombre}")
        print(f"   ✅ Duración: {carrera.duracion_semestres}")
        print(f"   ✅ Descripción: {carrera.descripcion[:50]}...")
        print(f"   ✅ Coordinador: {carrera.coordinador}")
        
        # Test 5: Obtener info
        print("\n5️⃣ Obteniendo información formateada...")
        info = carrera.obtener_info()
        print(f"\n   Respuesta que iría a WhatsApp:")
        print(f"   {'='*60}")
        print(info)
        print(f"   {'='*60}")
        
        print(f"\n   📊 Estadísticas:")
        print(f"      • Caracteres totales: {len(info)}")
        print(f"      • Líneas: {len(info.split(chr(10)))}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("✅ DEBUG COMPLETADO")
print("="*70)