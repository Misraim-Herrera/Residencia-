import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler # Mejor que StandardScaler para datos con ruido
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# 1. CARGAR Y LIMPIAR
import os
import pandas as pd

directorio_actual = os.path. dirname(os.path.abspath(__file__))
ruta_dataset = os.path.join(directorio_actual, "dataset_maestro_emg_ventaneado.csv")

df = pd.read_csv(ruta_dataset)

df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.dropna(inplace=True)


columnas_ruido = ["Movimiento"] 
X = df.drop(columns=["Movimiento"] + [c for c in columnas_ruido if c in df.columns])
y = df["Movimiento"]

# --- MEJORA 2: FILTRAR VALORES EXTREMOS (OUTLIERS) ---
# Si un valor es mayor a 3 desviaciones estándar, lo limita
for col in X.columns:
    limit = X[col].mean() + 3 * X[col].std()
    X[col] = X[col].clip(upper=limit)

# 2. DIVIDIR DATOS
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = RobustScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Reducimos un poco el tamaño para evitar que la red "alucine" con el ruido
mlp = MLPClassifier(
    hidden_layer_sizes=(64, 32), 
    max_iter=3000, 
    alpha=0.05,           # Regularización
    solver='adam', 
    activation='relu',
    random_state=42,
    learning_rate_init=0.001
)

print("Entrenando modelo de rescate... (esto debería mejorar el Movimiento 4)")
mlp.fit(X_train_scaled, y_train)

# EVALUACIÓN
predicciones = mlp.predict(X_test_scaled)
print("\n--- REPORTE DE CLASIFICACIÓN (ESTRATEGIA ROBUSTA) ---")
print(classification_report(y_test, predicciones))

# GUARDAR
joblib.dump(mlp, "modelo_emg_final.pkl")
joblib.dump(scaler, "escalador_emg_final.pkl")
print("\n[LISTO] Modelo guardado como 'modelo_emg_final.pkl'")