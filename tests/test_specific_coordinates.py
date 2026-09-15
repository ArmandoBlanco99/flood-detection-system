#!/usr/bin/env python3
"""Diagnostic for the specified coordinates: 19.4949629462, -99.1486655987
Test all four sensor values (0–3).
Command:
cd /Users/armyb/Documents/TT2 && /Users/armyb/Documents/TT2/.venv/bin/python tests/test_specific_coordinates.py"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from joblib import load
import pandas as pd


def test_specific_coordinates():
    """Test the requested specific coordinates."""

    # Load the model
    print("🔄 Cargando modelo...")
    model_path = os.path.join(os.path.dirname(__file__), "../src/predictive_model.pkl")
    model = load(model_path)
    print("✅ Modelo cargado")

    def get_zone_risk_score(lat, lon):
        input_data = pd.DataFrame([[lat, lon]], columns=["latitud", "longitud"])
        return model.predict(input_data)[0]

    def classify_zone_risk(score):
        if score <= 45:
            return "BAJO"
        elif score <= 65:
            return "MEDIO"
        else:
            return "ALTO"

    def is_within_mexico_city(lat, lon):
        return 19.35 <= lat <= 19.65 and -99.35 <= lon <= -98.95

    def predict_alert(lat, lon, sensor):
        risk_score = get_zone_risk_score(lat, lon)
        risk_level = classify_zone_risk(risk_score)

        if risk_level == "BAJO":
            alert = "VERDE" if sensor <= 2 else "AMARILLO"
        elif risk_level == "MEDIO":
            if sensor <= 1:
                alert = "VERDE"
            elif sensor == 2:
                alert = "AMARILLO"
            else:
                alert = "ROJO"
        else:  # HIGH
            if sensor == 0:
                alert = "VERDE"
            elif sensor == 1:
                alert = "AMARILLO"
            else:
                alert = "ROJO"

        return alert, risk_level, risk_score

    # Specific coordinates to test
    latitude = 19.526544451
    longitude = -99.165879364

    print("\n" + "=" * 70)
    print("🧪 PRUEBA DE COORDENADAS ESPECÍFICAS")
    print("=" * 70)
    print(f"📍 Coordenadas: ({latitude}, {longitude})")

    # Check whether the location is within Mexico City
    is_in_mexico_city = is_within_mexico_city(latitude, longitude)
    print(
        f"🗺️ Validación CDMX: {'✅ Dentro del rango' if is_in_mexico_city else '❌ Fuera del rango'}"
    )

    if not is_in_mexico_city:
        print("⚠️ ADVERTENCIA: Coordenada fuera del rango de CDMX")
        print("📍 Rango válido: Lat 19.35-19.65, Lon -99.35 a -98.95")
        print("🤖 La predicción puede no ser confiable")

    # Get baseline information about the zone
    risk_score = get_zone_risk_score(latitude, longitude)
    risk_level = classify_zone_risk(risk_score)

    print(f"\n🎯 ANÁLISIS DE LA ZONA:")
    print(f"   • Score de riesgo: {risk_score:.1f}")
    print(f"   • Clasificación: {risk_level}")

    # Check whether the coordinate exists in the dataset
    try:
        dataset_path = os.path.join(os.path.dirname(__file__), "../src/processed_dataset.csv")
        df = pd.read_csv(dataset_path)

        # Look for exact or nearby coordinates
        tolerance = 0.0001  # Approximately 11 meters
        nearby_coordinates = df[
            (abs(df["latitud"] - latitude) < tolerance)
            & (abs(df["longitud"] - longitude) < tolerance)
        ]

        if len(nearby_coordinates) > 0:
            row = nearby_coordinates.iloc[0]
            print(f"\n📊 DATOS DEL DATASET (encontrado):")
            print(f"   • Intensidad lluvia: {row['intensidad_mm']} mm")
            print(f"   • Área inundable: {row['area_inundable_pct']}%")
            print(f"   • Score dataset: {row['riesgo_zona_score']:.1f}")
            print(f"   • Clasificación dataset: {row['nivel_riesgo_zona']}")
            print(
                f"   • Diferencia con modelo: {abs(risk_score - row['riesgo_zona_score']):.1f} puntos"
            )
        else:
            print(f"\n📊 DATOS DEL DATASET: No se encontró esta coordenada exacta")
            print(f"   • El modelo hará interpolación basada en datos cercanos")

    except Exception as e:
        print(f"⚠️ No se pudo cargar el dataset: {e}")

    # Test every sensor level
    print(f"\n🚨 PREDICCIÓN DE ALERTAS POR NIVEL DE SENSOR:")
    print(f"{'Sensor':<8} {'Alerta':<10} {'Color':<6} {'Explicación'}")
    print("-" * 60)

    emojis = {"VERDE": "🟢", "AMARILLO": "🟡", "ROJO": "🔴"}
    explanations = {
        "VERDE": "Condiciones normales",
        "AMARILLO": "Precaución recomendada",
        "ROJO": "Peligro - Acción inmediata",
    }

    results = []
    for sensor in range(4):
        alert, level, score = predict_alert(latitude, longitude, sensor)
        emoji = emojis[alert]
        explanation = explanations[alert]

        print(f"{sensor:<8} {alert:<10} {emoji:<6} {explanation}")
        results.append(
            {
                "sensor": sensor,
                "alerta": alert,
                "emoji": emoji,
                "nivel_zona": level,
                "score": score,
            }
        )

    # Pattern analysis
    print(f"\n🔍 ANÁLISIS DE PATRONES:")
    green_alerts = sum(1 for r in results if r["alerta"] == "VERDE")
    yellow_alerts = sum(1 for r in results if r["alerta"] == "AMARILLO")
    red_alerts = sum(1 for r in results if r["alerta"] == "ROJO")

    print(f"   • Alertas VERDES: {green_alerts}/4 niveles de sensor")
    print(f"   • Alertas AMARILLAS: {yellow_alerts}/4 niveles de sensor")
    print(f"   • Alertas ROJAS: {red_alerts}/4 niveles de sensor")

    print(f"\n💡 INTERPRETACIÓN:")
    if risk_level == "BAJO":
        print(f"   • Zona de BAJO riesgo: Mayoría de sensores dan verde")
        print(f"   • Solo sensor nivel 3 debería dar amarillo")
    elif risk_level == "MEDIO":
        print(f"   • Zona de MEDIO riesgo: Escalado progresivo de alertas")
        print(f"   • Sensores 0-1: verde, sensor 2: amarillo, sensor 3: rojo")
    else:  # HIGH
        print(f"   • Zona de ALTO riesgo: Alertas más sensibles")
        print(f"   • Solo sensor 0: verde, sensor 1: amarillo, sensores 2-3: rojo")

    print("\n" + "=" * 70)
    print("✅ PRUEBA COMPLETADA")
    print("=" * 70)

    return results


if __name__ == "__main__":
    results = test_specific_coordinates()
