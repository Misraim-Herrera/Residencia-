import joblib
import numpy as np
import os

# --- CARGAR MODELO ---
ruta_modelo = "modelo_emg_final.pkl" 
if not os.path.exists(ruta_modelo):
    print(f"Error: No encuentro {ruta_modelo}")
    exit()

print(f"Cargando {ruta_modelo}...")
mlp = joblib.load(ruta_modelo)

# ARQUITECTURA
# 15 entradas -> 128 oculta -> 64 oculta -> 5 salidas
capas = mlp.coefs_
sesgos = mlp.intercepts_

print(f"Arquitectura detectada:")
print(f"  Entrada  -> Capa 1: {capas[0].shape} (Esperado: 15x128)")
print(f"  Capa 1   -> Capa 2: {capas[1].shape} (Esperado: 128x64)")
print(f"  Capa 2   -> Salida: {capas[2].shape} (Esperado: 64x5)")

# FUNCIÓN PARA GENERAR ARRAYS C++ 
def exportar_array(nombre, matriz):
    flat = matriz.flatten() # Aplanar matriz a vector 1D
    print(f"\n// Dimensiones originales: {matriz.shape}")
    print(f"const float {nombre}[{len(flat)}] = {{")
    # Imprimir valores formateados
    valores = ", ".join([f"{x:.6f}f" for x in flat])
    print(f"    {valores}")
    print("};")

print("\n" + "="*50)
print("   COPIA DESDE AQUÍ HACIA TU CÓDIGO C++ (.h)")
print("="*50)

# Exportar Pesos (Weights) y Sesgos (Biases)
exportar_array("W1", capas[0]) # Pesos Entrada -> Oculta 1
exportar_array("B1", sesgos[0]) # Sesgos Oculta 1

exportar_array("W2", capas[1]) # Pesos Oculta 1 -> Oculta 2
exportar_array("B2", sesgos[1]) # Sesgos Oculta 2

exportar_array("W3", capas[2]) # Pesos Oculta 2 -> Salida
exportar_array("B3", sesgos[2]) # Sesgos Salida

print("\n" + "="*50)