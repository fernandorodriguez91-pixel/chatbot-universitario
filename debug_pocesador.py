#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')

from services.procesador_lenguaje import ProcesadorLenguajeNatural
from models.mensaje import Mensaje, TipoMensaje

print("="*70)
print("🔍 DEBUG - PROCESADOR DE LENGUAJE")
print("="*70)

procesador = ProcesadorLenguajeNatural()

# Test 1: Limpiar texto
texto = "¿Qué información hay de Ingeniería Mecatrónica?"
print(f"\n1️⃣ Texto original:")
print(f"   '{texto}'")

texto_limpio = procesador.limpiar_texto(texto)
print(f"\n2️⃣ Texto limpio:")
print(f"   '{texto_limpio}'")

# Test 2: Verificar palabras clave de carrera
print(f"\n3️⃣ Palabras clave de carrera:")
print(f"   {procesador.palabras_carrera}")

# Test 3: Calcular score
print(f"\n4️⃣ Verificando palabras en texto limpio:")
for palabra in procesador.palabras_carrera:
    if palabra in texto_limpio:
        print(f"   ✅ Encontrada: '{palabra}'")
    else:
        print(f"   ❌ NO encontrada: '{palabra}'")

score_carrera = sum(1 for palabra in procesador.palabras_carrera if palabra in texto_limpio)
print(f"\n5️⃣ Score de carrera: {score_carrera}")

# Test 4: Extraer carrera
carrera_encontrada = procesador.extraer_carrera(texto)
print(f"\n6️⃣ Carrera extraída:")
print(f"   '{carrera_encontrada}'")

# Test 5: Clasificar mensaje
mensaje = Mensaje(telefono="1234567890", contenido=texto)
tipo = procesador.clasificar_mensaje(mensaje)
print(f"\n7️⃣ Tipo de mensaje clasificado:")
print(f"   {tipo}")
print(f"   ¿Es CONSULTA_CARRERA? {tipo == TipoMensaje.CONSULTA_CARRERA}")

# Test 6: Extraer intenciones
print(f"\n8️⃣ Intenciones extraídas:")
intenciones = procesador.extraer_intenciones(mensaje)
for key, value in intenciones.items():
    print(f"   {key}: {value}")

print("\n" + "="*70)
if tipo == TipoMensaje.CONSULTA_CARRERA and carrera_encontrada:
    print("✅ TODO CORRECTO - Debería devolver información de carrera")
else:
    print("❌ PROBLEMA DETECTADO:")
    if tipo != TipoMensaje.CONSULTA_CARRERA:
        print(f"   - Tipo de mensaje incorrecto: {tipo}")
    if not carrera_encontrada:
        print(f"   - Carrera NO fue extraída")
print("="*70)