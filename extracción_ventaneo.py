import os
import numpy as np
import pandas as pd


RUTA_SCRIPT = os.path.dirname(os.path.abspath(__file__))
os.chdir(RUTA_SCRIPT)


TAMANO_VENTANA = 250 
# Solapamiento: Avanzamos 100 puntos, lo que deja 150 puntos iguales a la ventana anterior
PASO_AVANCE = 100    

# FILTROS DIGITALES
def filtrar_señal(datos):

    datos = np.array(datos, dtype=float)
    datos = datos - np.mean(datos)
    
    x1, x2, y1, y2 = 0, 0, 0, 0
    nx1, nx2, ny1, ny2 = 0, 0, 0, 0
    filtrados = []
    
    # Coeficientes calculados (Notch 60Hz y Pasabanda 20-450Hz)
    b_n, a_n = [0.9636, -1.8001, 0.9636], [-1.8001, 0.9272]
    b_p, a_p = [0.5905, 0.0, -0.5905], [-0.1601, -0.1811]

    for x in datos:
        # Notch
        y_n = b_n[0]*x + b_n[1]*x1 + b_n[2]*x2 - a_n[0]*y1 - a_n[1]*y2
        x2, x1, y2, y1 = x1, x, y1, y_n
        # Pasabanda
        y_p = b_p[0]*y_n + b_p[1]*nx1 + b_p[2]*nx2 - a_p[0]*ny1 - a_p[1]*ny2
        nx2, nx1, ny2, ny1 = nx1, y_n, ny1, y_p
        filtrados.append(y_p)
    return np.array(filtrados)

# EXTRACCIÓN DE CARACTERÍSTICAS (CON LOGARITMOS)  
def extraer_17_features(s):
    diff_s = np.diff(s)
    N = len(s)
    
    # Características de Amplitud
    mav = np.mean(np.abs(s))
    mav1 = np.mean(np.where((np.arange(N) >= 0.25*N) & (np.arange(N) <= 0.75*N), 1, 0.5) * np.abs(s))
    mav2 = np.mean(np.where((np.arange(N) >= 0.25*N) & (np.arange(N) <= 0.75*N), 1, 
                  np.where(np.arange(N) < 0.25*N, 4*np.arange(N)/N, 4*(np.arange(N)-N)/N)) * np.abs(s))
    rms = np.sqrt(np.mean(s**2))
    var = np.var(s)
    ssi = np.sum(s**2)
    wl = np.sum(np.abs(diff_s))
    
    # Cruces por cero y cambios de signo (ZC, SSC, WAMP)
    umbral = 0.05 
    zc = len(np.where(np.diff(np.sign(s[np.abs(s) > umbral])))[0])
    ssc = len(np.where(np.diff(np.sign(diff_s[np.abs(diff_s) > umbral])))[0])
    wamp = np.sum(np.abs(diff_s) > umbral)
    
    aac = np.mean(np.abs(diff_s))
    dasdv = np.sqrt(np.mean(diff_s**2))
    
    # LOG y MYOP
    log_feat = np.log10(np.abs(np.mean(np.log(np.abs(s) + 1e-10))) + 1)
    myop = np.sum(np.abs(s) > umbral) / N
    
    # Momentos Temporales con LOGARITMO 
    tm3 = np.log10(np.abs(np.mean(s**3)) + 1)
    tm4 = np.log10(np.abs(np.mean(s**4)) + 1)
    tm5 = np.log10(np.abs(np.mean(s**5)) + 1)

    return [mav, mav1, mav2, rms, var, ssi, wl, zc, ssc, wamp, aac, dasdv, log_feat, myop, tm3, tm4, tm5]

# PROCESAMIENTO GENERAL CON VENTANEO 
def generar_dataset():
    columnas = ["MAV", "MAV1", "MAV2", "RMS", "VAR", "SSI", "WL", "ZC", "SSC", "WAMP", 
                "AAC", "DASDV", "LOG", "MYOP", "TM3", "TM4", "TM5", "Movimiento"]
    dataset = []

    carpetas = [d for d in os.listdir('.') if os.path.isdir(d) and "datos" in d.lower()]
    
    if not carpetas:
        print("\n[ERROR] No se encontraron carpetas con 'datos'.")
        return

    for carpeta in carpetas:
        print(f"\n>>> Procesando Carpeta: {carpeta}")
        archivos = [f for f in os.listdir(carpeta) if f.lower().endswith('.csv')]
        archivos.sort()

        for i, archivo in enumerate(archivos):
            ruta = os.path.join(carpeta, archivo)
            try:
                # 1. Cargar la señal completa
                raw = np.loadtxt(ruta, delimiter=',') 
                limpio = filtrar_señal(raw)
                
                # VETANEO
                num_puntos = len(limpio)
                
                if num_puntos >= TAMANO_VENTANA:
                    contador_ventanas = 0
                    
                    for inicio in range(0, num_puntos - TAMANO_VENTANA, PASO_AVANCE):
                        fin = inicio + TAMANO_VENTANA
                        ventana = limpio[inicio:fin]
                        
                        # Extraer características de esta ventana
                        features = extraer_17_features(ventana)
                        
                        features.append(i + 1) 
                        dataset.append(features)
                        contador_ventanas += 1
                        
                    print(f"  [OK] {archivo} -> Mov: {i+1} | Generó {contador_ventanas} ventanas")
                else:
                    print(f"  [Warn] {archivo} es muy corto ({num_puntos} pts), se ignora.")
                    
            except Exception as e:
                print(f"  [Error] {archivo}: {e}")

    if dataset:
        df = pd.DataFrame(dataset, columns=columnas)
        # Limpieza final 
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.dropna(inplace=True)
        
        df.to_csv("dataset_maestro_emg_ventaneado.csv", index=False)
        print(f"\n[ÉXITO TOTAL] Dataset generado con {len(df)} filas.")
        print("Usa 'dataset_maestro_emg_ventaneado.csv' para entrenar tu modelo.")
    else:
        print("\n[AVISO] No se generaron datos. Revisa tus archivos CSV.")

if __name__ == "__main__":
    generar_dataset()