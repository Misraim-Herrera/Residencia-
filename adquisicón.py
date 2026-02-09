import machine
import utime
import sys
import os
import struct  

# --- 1. Configuración de Hardware ---
adc = machine.ADC(26)  # Pin del AD8232
SAMPLING_RATE = 1000   # 1000 Hz
PERIOD_MS = 1          # 1 ms

# --- 2. Variables y Configuración ---
movimientos = [4, 2, 6, 2, 4] 
data_buffer = []
sampling_active = False

# Función de guardado (Binario)
def save_to_file(filename, data):
    filename = filename.replace(".csv", ".bin")
    print(f"\n[SISTEMA] Guardando {len(data)} muestras en {filename}...")
    
    try:
        with open(filename, "wb") as f:  # "wb" para escritura binaria
            for value in data:
                # '<H' empaqueta como unsigned short (2 bytes) en formato little-endian
                f.write(struct.pack('<H', value))
        print("[SISTEMA] Guardado binario exitoso.")
    except Exception as e:
        print(f"Error crítico al guardar (posible memoria llena): {e}")

# Interrupción del Timer 
def sample_callback(timer):
    global sampling_active, data_buffer
    if sampling_active:
       
        data_buffer.append(adc.read_u16())

timer = machine.Timer()

#  Inicio del Programa
print("\n--- ADQUISICIÓN EMG: MODO ALTA EFICIENCIA (BINARIO) ---")
sesion_id = input("Introduce el ID de esta toma: ")

nombre_carpeta = "datos_s" + sesion_id
try:
    os.mkdir(nombre_carpeta)
    print(f"[SISTEMA] Carpeta '{nombre_carpeta}' creada.")
except:
    print(f"[SISTEMA] Carpeta: '{nombre_carpeta}'")

for i, duracion in enumerate(movimientos):
    print(f"\n>>> LISTO: MOVIMIENTO {i+1} ({duracion}s)")
    input(">>> Presiona ENTER para iniciar captura...")
    
    data_buffer = [] 
    samples_to_collect = duracion * SAMPLING_RATE
    
    # Iniciar captura
    sampling_active = True
    timer.init(period=PERIOD_MS, mode=machine.Timer.PERIODIC, callback=sample_callback)
    
    # ESPERA PASIVA:
    print( "Capturando datos...", end="\r")
    while len(data_buffer) < samples_to_collect:
        utime.sleep_ms(100) # Dormimos un poco para no saturar la CPU
    
    # Detener captura
    timer.deinit()
    sampling_active = False
    
    nombre_archivo = f"{nombre_carpeta}/s{sesion_id}_mov{i+1}_{duracion}s.bin"
    save_to_file(nombre_archivo, data_buffer)

print("\n--- PROCESO TERMINADO ---")