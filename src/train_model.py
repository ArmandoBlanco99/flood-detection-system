import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from joblib import dump
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

# 1) Load the processed dataset with coordinates and numeric values
print("🔄 Cargando dataset procesado...")
df = pd.read_csv("processed_dataset.csv")

print("📊 Primeras filas del dataset:")
print(df.head())
print(f"\n📈 Dataset: {len(df)} ubicaciones únicas")
print(f"📍 Rango de coordenadas:")
print(f"   • Latitud: {df['latitud'].min():.6f} a {df['latitud'].max():.6f}")
print(f"   • Longitud: {df['longitud'].min():.6f} a {df['longitud'].max():.6f}")
print(
    f"⚡ Rango de riesgo: {df['riesgo_zona_score'].min():.1f} a {df['riesgo_zona_score'].max():.1f}"
)

print(f"\n🎯 Distribución por nivel de riesgo de zona:")
print(df["nivel_riesgo_zona"].value_counts())

# 2) Define features (X) and target (y)
# INPUT: [latitud, longitud] -> OUTPUT: riesgo_zona_score
X = df[["latitud", "longitud"]]
y = df["riesgo_zona_score"]

print(f"\n🧠 Configuración del modelo:")
print(f"   • Entradas: {list(X.columns)}")
print(f"   • Salida: riesgo_zona_score (continuo)")
print(f"   • Algoritmo: Random Forest Regressor")

# 3) Split into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4) Create and train the Random Forest regressor
print(f"\n🚀 Entrenando modelo...")
model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
model.fit(X_train, y_train)

# 5) Evaluate the model
y_pred = model.predict(X_test)

print(f"\n📊 Evaluación del modelo:")
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"   • Error cuadrático medio: {mse:.2f}")
print(f"   • R² Score: {r2:.3f}")
print(f"   • Error promedio: ±{np.sqrt(mse):.2f} puntos de riesgo")

# 6) Display feature importance
feature_importance = model.feature_importances_
print(f"\n🎯 Importancia de características:")
for i, feature in enumerate(X.columns):
    print(f"   • {feature}: {feature_importance[i]:.3f}")

# 7) Plot predicted versus actual values
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred, alpha=0.6)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], "r--", lw=2)
plt.xlabel("Riesgo Real")
plt.ylabel("Riesgo Predicho")
plt.title("Predicciones vs Valores Reales - Riesgo de Zona")
plt.grid(True, alpha=0.3)
plt.show()

# 8) Save the trained model
try:
    # When running the file directly
    script_dir = Path(__file__).resolve().parent
    model_path = script_dir / "predictive_model.pkl"
except NameError:
    # When running a snippet without __file__
    model_path = Path("predictive_model.pkl")

dump(model, model_path)
print(f"\n💾 Modelo guardado como: 'predictive_model.pkl'")

print(f"\n✅ Modelo entrenado y guardado exitosamente!")
print(f"🔄 Para usar el modelo, ejecuta: python3 realtime.py")
print(f"🌐 Para el servidor web, ejecuta: python3 flask_server.py")
