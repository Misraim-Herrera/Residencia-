import joblib
import numpy as np
import os

# Cargar el escalador entrenado
directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_scaler = os.path.join(directorio_actual, "escalador_emg_final.pkl")

print(f"Cargando {ruta_scaler}...")
scaler = joblib.load(ruta_scaler)


medianas = scaler.center_
escalas = scaler.scale_

# Verificar que sean 15 características
if len(medianas) != 15:
    print(f"¡ALERTA! El escalador tiene {len(medianas)} características, pero esperábamos 15.")
else:
    print("¡Correcto! El escalador tiene 15 características.")

# --- GENERAR CÓDIGO C++ ---
print("\n" + "="*40)
print("="*40 + "\n")

print("// --- PARÁMETROS DEL ROBUST SCALER")
print(f"const float SCALER_MEDIAN[{len(medianas)}] = {{")
print("    " + ", ".join([f"{x:.6f}f" for x in medianas]))
print("};")

print(f"\nconst float SCALER_IQ[{len(escalas)}] = {{")
print("    " + ", ".join([f"{x:.6f}f" for x in escalas]))
print("};")

print("\n" + "="*40)