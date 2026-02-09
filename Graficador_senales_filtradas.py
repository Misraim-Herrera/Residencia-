import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# CONFIGURACIÓN

RUTA_CARPETA = r'C:\Users\misra\OneDrive\Desktop\RESIDENCIA\MicroPico\Muestras_CSV\datos_s18' 

FS = 1000.0  # Frecuencia de muestreo (1000 Hz)

def diseñar_filtros():
    """
  
    """
    # --- FILTRO NOTCH (60Hz) ---

    f0 = 60.0  
    Q = 30.0  
    b_notch, a_notch = signal.iirnotch(f0, Q, FS)

    # --- FILTRO PASABANDA (20-450Hz) ---
  
    lowcut = 20.0
    highcut = 450.0
    nyquist = 0.5 * FS
    low = lowcut / nyquist
    high = highcut / nyquist
    b_band, a_band = signal.butter(2, [low, high], btype='band')
    
    return (b_notch, a_notch), (b_band, a_band)

def procesar_carpeta(ruta):
    # Obtener lista de archivos CSV
    archivos = [f for f in os.listdir(ruta) if f.endswith('.csv')]
    archivos.sort() # Ordenar alfabéticamente
    
    if not archivos:
        print(f"No se encontraron archivos .csv en: {ruta}")
        return

    archivos_a_procesar = archivos[:5]
    
    # Obtener coeficientes
    (b_notch, a_notch), (b_band, a_band) = diseñar_filtros()

    # Configurar la figura (5 subgráficas verticales)
    fig, axes = plt.subplots(len(archivos_a_procesar), 1, figsize=(10, 12), sharex=True)
    
    if len(archivos_a_procesar) == 1:
        axes = [axes]

    print(f"Procesando {len(archivos_a_procesar)} archivos...")

    for i, archivo in enumerate(archivos_a_procesar):
        ruta_completa = os.path.join(ruta, archivo)
        
        # CARGAR DATOS 

        try:
            df = pd.read_csv(ruta_completa, header=None)
            
            raw_signal = df.iloc[:, 0].values 
            
            # Crear eje de tiempo
            t = np.arange(len(raw_signal)) / FS
            
            # APLICAR FILTROS (Simulación del Microcontrolador)
            # 1. Aplicar Notch
            signal_notch = signal.lfilter(b_notch, a_notch, raw_signal)
            
            # 2. Aplicar Pasabanda (sobre la señal ya filtrada por Notch)
            signal_clean = signal.lfilter(b_band, a_band, signal_notch)

            # --- GRAFICAR ---
            ax = axes[i]
            
            # Graficar señal cruda 
            ax.plot(t, raw_signal, color='lightgray', label='Señal Cruda (Raw)', alpha=0.7)
            
            # Graficar señal filtrada 
            ax.plot(t, signal_clean, color='#007acc', label='Filtrada (Notch + Bandpass)', linewidth=1.5)
            
            ax.set_title(f"Archivo: {archivo}", fontsize=10, fontweight='bold')
            ax.set_ylabel("Amplitud *", fontsize=9)
            ax.legend(loc='upper right', fontsize=8)
            ax.grid(True, linestyle='--', alpha=0.5)

        except Exception as e:
            print(f"Error procesando {archivo}: {e}")

    plt.xlabel("Tiempo (s)")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    procesar_carpeta(RUTA_CARPETA)