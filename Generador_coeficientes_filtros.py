import numpy as np
from scipy import signal

# --- 1. CONFIGURACIÓN GENERAL ---
fs = 1000.0  # Frecuencia de muestreo (Hz)

# --- 2. DISEÑO FILTRO NOTCH (60 Hz) ---
# Tipo: IIR Notch (2do Orden)
f0 = 60.0   # Frecuencia de corte (ruido eléctrico)
Q = 30.0    # Factor de calidad (mientras más alto, más estrecha la muesca)

# La función iirnotch devuelve los coeficientes b (numerador) y a (denominador)
b_notch, a_notch = signal.iirnotch(f0, Q, fs)

# --- 3. DISEÑO FILTRO PASABANDA (20-450 Hz) ---
# Tipo: Butterworth
# Orden: 2 (Al ser pasabanda, esto genera un sistema de 4to orden total)
lowcut = 20.0
highcut = 450.0

# signal.butter diseña el filtro. 
# 'btype' define que es pasabanda. 
# 'output'='ba' devuelve numerador y denominador.
b_band, a_band = signal.butter(2, [lowcut, highcut], btype='band', fs=fs)

# --- 4. IMPRESIÓN CON FORMATO C++ ---
# Esta función imprime los valores finales
def imprimir_para_cpp(nombre, b, a):
    print(f"\n// --- Coeficientes Filtro {nombre} ---")
    print("// Numerador (b)")
    for i, val in enumerate(b):
        # Usamos .8f para tener 8 decimales de precisión (double)
        print(f"const double {nombre}_b{i} = {val:.8f};")
        
    print("// Denominador (a)")
    for i, val in enumerate(a):
        print(f"const double {nombre}_a{i} = {val:.8f};")

print("Copie estos valores en su código C++:")
imprimir_para_cpp("notch", b_notch, a_notch)
imprimir_para_cpp("pasabanda", b_band, a_band)