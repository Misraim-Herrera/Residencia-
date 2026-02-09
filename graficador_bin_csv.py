import struct
import matplotlib.pyplot as plt
import os
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ruta_sesion = os.path.join(BASE_DIR, "datos_s18")

def cargar_datos_emg(ruta_archivo):
    """Detecta el formato (.bin o .csv) y carga los datos."""
    _, extension = os.path.splitext(ruta_archivo)
    datos = []
    try:
        if extension.lower() == '.bin':
            with open(ruta_archivo, "rb") as f:
                contenido = f.read()
                num_muestras = len(contenido) // 2
                datos = list(struct.unpack(f'<{num_muestras}H', contenido))
        elif extension.lower() == '.csv':
            with open(ruta_archivo, "r") as f:
                for linea in f:
                    limpia = linea.strip().replace('(', '').replace(')', '').replace(',', '')
                    if limpia: datos.append(int(limpia))
        return datos
    except Exception as e:
        print(f"Error al leer {ruta_archivo}: {e}")
        return None

def graficar_sesion(ruta_carpeta):
    # 1. Obtener y ordenar archivos de la carpeta
    archivos = [f for f in os.listdir(ruta_carpeta) if f.endswith(('.bin', '.csv'))]
    archivos.sort() # Los ordena por nombre (mov1, mov2, mov3...)

    if not archivos:
        print("No se encontraron archivos .bin o .csv en la carpeta.")
        return

    # 2. Configurar la figura con subplots
    fig, axes = plt.subplots(len(archivos), 1, figsize=(12, 2 * len(archivos)), sharex=False)
    fig.subplots_adjust(hspace=0.5)
    fig.suptitle(f"Sesión: {os.path.basename(ruta_carpeta)}", fontsize=16)

    if len(archivos) == 1: axes = [axes]

    # 3. Cargar y graficar cada movimiento
    for i, archivo in enumerate(archivos):
        ruta_completa = os.path.join(ruta_carpeta, archivo)
        valores = cargar_datos_emg(ruta_completa)
        
        if valores:
            axes[i].plot(valores, color='#2980b9', linewidth=0.7)
            axes[i].set_title(f"Movimiento: {archivo}", fontsize=10)
            axes[i].grid(True, alpha=0.3)
            axes[i].set_ylabel("ADC")

    plt.xlabel("Muestras (1000 Hz)")
    plt.show()
-
ruta_sesion = r"C:\Users\misra\OneDrive\Desktop\RESIDENCIA\MicroPico\Muestras_CSV\datos_s1"
 
graficar_sesion(ruta_sesion)