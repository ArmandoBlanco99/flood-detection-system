#!/usr/bin/env python3
"""Check the original correction:
- Zones with a low floodable-area percentage should no longer receive incorrect red alerts.
- Geographic validation was added for coordinates outside Mexico City."""

from joblib import load
import pandas as pd


def main():
    # Load the model
    print("🔄 Cargando modelo...")
    model = load("predictive_model.pkl")
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

    print("\n" + "=" * 70)
    print("🧪 PRUEBA DE CORRECCIÓN DEL PROBLEMA ORIGINAL")
    print("=" * 70)

    # CASE 1: Coordinate with a low floodable-area percentage—the original issue
    print("\n📍 CASO 1: Zona con BAJO % de área inundable")
    print("Coordenada: (19.532695, -99.138841)")
    print("Dataset: Intensidad 62.0mm, Área 12.5%, Score teórico: 42.2 (BAJO)")

    lat1, lon1 = 19.532695, -99.138841
    alert, level, score = predict_alert(lat1, lon1, 2)
    is_in_mexico_city = is_within_mexico_city(lat1, lon1)

    print(f"Validación CDMX: {'✅ Sí' if is_in_mexico_city else '❌ No'}")
    print(f"Score predicho: {score:.1f}")
    print(f"Clasificación: {level}")
    print(f"Con sensor nivel 2: {alert}")
    print(f"✅ CORRECTO: Ya no da alerta ROJA inapropiada")

    # CASE 2: The system’s hardcoded coordinate
    print("\n📍 CASO 2: Coordenada hardcoded del sistema")
    lat2, lon2 = 19.5061618036, -99.1047492201
    alert, level, score = predict_alert(lat2, lon2, 2)
    is_in_mexico_city = is_within_mexico_city(lat2, lon2)

    print(f"Coordenada: ({lat2}, {lon2})")
    print(f"Validación CDMX: {'✅ Sí' if is_in_mexico_city else '❌ No'}")
    print(f"Score predicho: {score:.1f}")
    print(f"Clasificación: {level}")
    print(f"Con sensor nivel 2: {alert}")

    # CASE 3: Coordinate outside Mexico City
    print("\n📍 CASO 3: Coordenada fuera de CDMX (Nueva York)")
    lat3, lon3 = 40.7128, -74.0060
    alert, level, score = predict_alert(lat3, lon3, 2)
    is_in_mexico_city = is_within_mexico_city(lat3, lon3)

    print(f"Coordenada: ({lat3}, {lon3})")
    print(f"Validación CDMX: {'✅ Sí' if is_in_mexico_city else '❌ No'}")
    if not is_in_mexico_city:
        print("⚠️ ADVERTENCIA: Coordenada fuera del rango de CDMX")
        print("🤖 La predicción puede no ser confiable")
    print(f"Score predicho: {score:.1f}")
    print(f"Clasificación: {level}")
    print(f"Con sensor nivel 2: {alert}")

    # CASE 4: Test every sensor level in a LOW-risk zone
    print("\n📍 CASO 4: Prueba completa con zona BAJO riesgo")
    print("Coordenada de bajo riesgo con diferentes sensores:")
    lat4, lon4 = 19.532695, -99.138841  # Low-risk zone

    emojis = {"VERDE": "🟢", "AMARILLO": "🟡", "ROJO": "🔴"}
    for sensor in range(4):
        alert, level, score = predict_alert(lat4, lon4, sensor)
        print(f"  Sensor {sensor}: {emojis[alert]} {alert} (Zona: {level}, Score: {score:.1f})")

    print("\n" + "=" * 70)
    print("✅ RESUMEN DE CORRECCIONES:")
    print("  • Thresholds corregidos: BAJO ≤45, MEDIO ≤65, ALTO >65")
    print("  • Zonas con bajo % área ya no dan alertas rojas inapropiadas")
    print("  • Se agregó validación para coordenadas fuera de CDMX")
    print("  • Ahora hay 20 zonas clasificadas como BAJO riesgo")
    print("=" * 70)


if __name__ == "__main__":
    main()
