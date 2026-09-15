#!/usr/bin/env python3
"""
Test para coordenadas específicas: 19.4949629462, -99.1486655987
Prueba con los 4 valores del sensor (0-3)
cmd:
cd /Users/armyb/Documents/TT2 && /Users/armyb/Documents/TT2/.venv/bin/python tests/test_coordenadas_especificas.py
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from joblib import load
import pandas as pd


def test_coordenadas_especificas():
    """Prueba las coordenadas específicas solicitadas"""

    # Cargar modelo
    print("🔄 Cargando modelo...")
    modelo_path = os.path.join(os.path.dirname(__file__), "../src/modelo_predictivo.pkl")
    modelo = load(modelo_path)
    print("✅ Modelo cargado")

    def obtener_riesgo_zona(lat, lon):
        input_data = pd.DataFrame([[lat, lon]], columns=["latitud", "longitud"])
        return modelo.predict(input_data)[0]

    def clasificar_riesgo_zona(score):
        if score <= 45:
            return "BAJO"
        elif score <= 65:
            return "MEDIO"
        else:
            return "ALTO"

    def validar_coordenadas_cdmx(lat, lon):
        return 19.35 <= lat <= 19.65 and -99.35 <= lon <= -98.95

    def predecir_alerta(lat, lon, sensor):
        riesgo_score = obtener_riesgo_zona(lat, lon)
        nivel_riesgo = clasificar_riesgo_zona(riesgo_score)

        if nivel_riesgo == "BAJO":
            alerta = "VERDE" if sensor <= 2 else "AMARILLO"
        elif nivel_riesgo == "MEDIO":
            if sensor <= 1:
                alerta = "VERDE"
            elif sensor == 2:
                alerta = "AMARILLO"
            else:
                alerta = "ROJO"
        else:  # ALTO
            if sensor == 0:
                alerta = "VERDE"
            elif sensor == 1:
                alerta = "AMARILLO"
            else:
                alerta = "ROJO"

        return alerta, nivel_riesgo, riesgo_score

    # Coordenadas específicas a probar
    latitud = 19.526544451
    longitud = -99.165879364

    print("\n" + "=" * 70)
    print("🧪 PRUEBA DE COORDENADAS ESPECÍFICAS")
    print("=" * 70)
    print(f"📍 Coordenadas: ({latitud}, {longitud})")

    # Validar si está en CDMX
    en_cdmx = validar_coordenadas_cdmx(latitud, longitud)
    print(f"🗺️ Validación CDMX: {'✅ Dentro del rango' if en_cdmx else '❌ Fuera del rango'}")

    if not en_cdmx:
        print("⚠️ ADVERTENCIA: Coordenada fuera del rango de CDMX")
        print("📍 Rango válido: Lat 19.35-19.65, Lon -99.35 a -98.95")
        print("🤖 La predicción puede no ser confiable")

    # Obtener información base de la zona
    riesgo_score = obtener_riesgo_zona(latitud, longitud)
    nivel_riesgo = clasificar_riesgo_zona(riesgo_score)

    print(f"\n🎯 ANÁLISIS DE LA ZONA:")
    print(f"   • Score de riesgo: {riesgo_score:.1f}")
    print(f"   • Clasificación: {nivel_riesgo}")

    # Verificar si esta coordenada está en el dataset
    try:
        dataset_path = os.path.join(os.path.dirname(__file__), "../src/dataset_procesado.csv")
        df = pd.read_csv(dataset_path)

        # Buscar coordenadas exactas o muy cercanas
        tolerancia = 0.0001  # Aproximadamente 11 metros
        coordenadas_cercanas = df[
            (abs(df["latitud"] - latitud) < tolerancia)
            & (abs(df["longitud"] - longitud) < tolerancia)
        ]

        if len(coordenadas_cercanas) > 0:
            row = coordenadas_cercanas.iloc[0]
            print(f"\n📊 DATOS DEL DATASET (encontrado):")
            print(f"   • Intensidad lluvia: {row['intensidad_mm']} mm")
            print(f"   • Área inundable: {row['area_inundable_pct']}%")
            print(f"   • Score dataset: {row['riesgo_zona_score']:.1f}")
            print(f"   • Clasificación dataset: {row['nivel_riesgo_zona']}")
            print(
                f"   • Diferencia con modelo: {abs(riesgo_score - row['riesgo_zona_score']):.1f} puntos"
            )
        else:
            print(f"\n📊 DATOS DEL DATASET: No se encontró esta coordenada exacta")
            print(f"   • El modelo hará interpolación basada en datos cercanos")

    except Exception as e:
        print(f"⚠️ No se pudo cargar el dataset: {e}")

    # Probar con todos los niveles de sensor
    print(f"\n🚨 PREDICCIÓN DE ALERTAS POR NIVEL DE SENSOR:")
    print(f"{'Sensor':<8} {'Alerta':<10} {'Color':<6} {'Explicación'}")
    print("-" * 60)

    emojis = {"VERDE": "🟢", "AMARILLO": "🟡", "ROJO": "🔴"}
    explicaciones = {
        "VERDE": "Condiciones normales",
        "AMARILLO": "Precaución recomendada",
        "ROJO": "Peligro - Acción inmediata",
    }

    resultados = []
    for sensor in range(4):
        alerta, nivel, score = predecir_alerta(latitud, longitud, sensor)
        emoji = emojis[alerta]
        explicacion = explicaciones[alerta]

        print(f"{sensor:<8} {alerta:<10} {emoji:<6} {explicacion}")
        resultados.append(
            {
                "sensor": sensor,
                "alerta": alerta,
                "emoji": emoji,
                "nivel_zona": nivel,
                "score": score,
            }
        )

    # Análisis de patrones
    print(f"\n🔍 ANÁLISIS DE PATRONES:")
    alertas_verde = sum(1 for r in resultados if r["alerta"] == "VERDE")
    alertas_amarillo = sum(1 for r in resultados if r["alerta"] == "AMARILLO")
    alertas_rojo = sum(1 for r in resultados if r["alerta"] == "ROJO")

    print(f"   • Alertas VERDES: {alertas_verde}/4 niveles de sensor")
    print(f"   • Alertas AMARILLAS: {alertas_amarillo}/4 niveles de sensor")
    print(f"   • Alertas ROJAS: {alertas_rojo}/4 niveles de sensor")

    print(f"\n💡 INTERPRETACIÓN:")
    if nivel_riesgo == "BAJO":
        print(f"   • Zona de BAJO riesgo: Mayoría de sensores dan verde")
        print(f"   • Solo sensor nivel 3 debería dar amarillo")
    elif nivel_riesgo == "MEDIO":
        print(f"   • Zona de MEDIO riesgo: Escalado progresivo de alertas")
        print(f"   • Sensores 0-1: verde, sensor 2: amarillo, sensor 3: rojo")
    else:  # ALTO
        print(f"   • Zona de ALTO riesgo: Alertas más sensibles")
        print(f"   • Solo sensor 0: verde, sensor 1: amarillo, sensores 2-3: rojo")

    print("\n" + "=" * 70)
    print("✅ PRUEBA COMPLETADA")
    print("=" * 70)

    return resultados


if __name__ == "__main__":
    resultados = test_coordenadas_especificas()
