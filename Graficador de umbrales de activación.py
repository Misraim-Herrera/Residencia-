import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

file_path = 'valores de umbrales.txt'

with open(file_path, 'r') as f:
    lines = f.readlines()

data = {
    "rest": [],
    "medium": [],
    "high": []
}

current_category = None

for line in lines:
    line = line.strip()
    if "movimiento en reposo" in line.lower():
        current_category = "rest"
    elif "flexion media" in line.lower():
        current_category = "medium"
    elif "flexion total" in line.lower():
        current_category = "high"
    elif "cerró el puerto" in line.lower():
        current_category = None
    else:

        try:
            val = float(line)
            if current_category:
                data[current_category].append(val)
        except ValueError:
            continue


for key in data:
    data[key] = np.array(data[key])


stats = {}
for key, values in data.items():
    if len(values) > 0:
        stats[key] = {
            "min": np.min(values),
            "max": np.max(values),
            "mean": np.mean(values),
            "median": np.median(values),
            "p95": np.percentile(values, 95),
            "p5": np.percentile(values, 5),
            "p99": np.percentile(values, 99),
            "p1": np.percentile(values, 1)
        }


threshold_medio_raw = (stats['rest']['p99'] + stats['medium']['p5']) / 2


threshold_alto_raw = (stats['medium']['p95'] + stats['high']['p5']) / 2

plt.figure(figsize=(12, 6))
plt.plot(data['rest'], label='Reposo (Rest)', color='green', alpha=0.6)

idx_start_med = len(data['rest'])
plt.plot(range(idx_start_med, idx_start_med + len(data['medium'])), data['medium'], label='Flexión Media (Medium)', color='orange', alpha=0.6)

idx_start_high = idx_start_med + len(data['medium'])
plt.plot(range(idx_start_high, idx_start_high + len(data['high'])), data['high'], label='Flexión Total (High)', color='red', alpha=0.6)

plt.axhline(y=threshold_medio_raw, color='blue', linestyle='--', linewidth=2, label=f'Umbral Medio Calc: {threshold_medio_raw:.1f}')
plt.axhline(y=threshold_alto_raw, color='purple', linestyle='--', linewidth=2, label=f'Umbral Alto Calc: {threshold_alto_raw:.1f}')

plt.title('Análisis de Señal EMG y Definición de Umbrales')
plt.xlabel('Muestras')
plt.ylabel('Amplitud de Energía')
plt.legend()
plt.grid(True, alpha=0.3)

plot_filename = 'emg_thresholds_analysis.png'
plt.savefig(plot_filename)

print(stats)
print(f"Propuesta Umbral Medio: {threshold_medio_raw}")
print(f"Propuesta Umbral Alto: {threshold_alto_raw}")