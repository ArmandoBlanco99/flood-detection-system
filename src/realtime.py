from joblib import load
import pandas as pd
from pathlib import Path

# 1) Load the trained model
script_dir = Path(__file__).resolve().parent
model_path = script_dir / "predictive_model.pkl"

try:
    model = load(model_path)
    print("✅ Modelo cargado exitosamente")
except FileNotFoundError:
    print("❌ Error: No se encontró 'predictive_model.pkl'")
    print("🔄 Ejecuta primero: python3 train_model.py")
    exit(1)


def is_within_mexico_city(latitude, longitude):
    """Check whether coordinates fall within the approximate Mexico City bounds.

    Args:
        latitude (float): Location latitude.
        longitude (float): Location longitude.

    Returns:
        bool: True when within Mexico City, otherwise False."""
    # Approximate Mexico City bounds based on the dataset
    LAT_MIN, LAT_MAX = 19.35, 19.65
    LON_MIN, LON_MAX = -99.35, -98.95

    return LAT_MIN <= latitude <= LAT_MAX and LON_MIN <= longitude <= LON_MAX


def get_zone_risk_score(latitude, longitude):
    """Predict zone risk from geographic coordinates.
    First search the dataset for a coordinate match within the tolerance;
    otherwise, use the prediction model.

    Args:
        latitude (float): Location latitude.
        longitude (float): Location longitude.

    Returns:
        float: Zone risk score (39.2–77.2)."""
    # Check whether the coordinates are within Mexico City
    if not is_within_mexico_city(latitude, longitude):
        print(
            f"⚠️ ADVERTENCIA: Las coordenadas ({latitude}, {longitude}) están fuera del rango de CDMX"
        )
        print(f"📍 Rango válido: Lat 19.35-19.65, Lon -99.35 a -98.95")
        print(f"🤖 La predicción puede no ser confiable para ubicaciones fuera de CDMX")

    # IMPROVEMENT: First check the dataset for this coordinate
    # Tolerance of ±0.0001 degrees, approximately 10 meters
    dataset = pd.read_csv(script_dir / "processed_dataset.csv")
    match = dataset[
        (abs(dataset["latitud"] - latitude) < 0.0001)
        & (abs(dataset["longitud"] - longitude) < 0.0001)
    ]

    if not match.empty:
        # Use the dataset value when the coordinate is found
        risk_score = match["riesgo_zona_score"].iloc[0]
        print(f"🎯 Coordenada encontrada en dataset → Score: {risk_score:.1f}")
        return risk_score

    # Use the prediction model when there is no dataset match
    print(f"🔮 Coordenada no en dataset → Usando modelo de predicción")
    input_data = pd.DataFrame([[latitude, longitude]], columns=["latitud", "longitud"])
    risk_score = model.predict(input_data)[0]
    return risk_score


def classify_zone_risk(risk_score):
    """Classify the risk score into categories.

    Args:
        risk_score (float): Risk score.

    Returns:
        str: Risk level ('BAJO', 'MEDIO', 'ALTO')."""
    if risk_score <= 45:
        return "BAJO"
    elif risk_score <= 65:
        return "MEDIO"
    else:
        return "ALTO"


# Hardcoded LOW-risk coordinates
# FIXED_LATITUDE = 19.5061618036
# FIXED_LONGITUDE = -99.1047492201
# Hardcoded HIGH-risk coordinates 19.5228166649,-99.1678551529
FIXED_LATITUDE = 19.5228166649
FIXED_LONGITUDE = -99.1678551529
# UPIITA coordinates 19.5113119,-99.1251155
# FIXED_LATITUDE = 19.5113119
# FIXED_LONGITUDE = -99.1251155
# Hardcoded MEDIUM-risk coordinate 19.5041017692,-99.0986932319
# FIXED_LATITUDE = 19.5041017692
# FIXED_LONGITUDE = -99.0986932319


def predict_alert(sensor_level):
    """Predict the alert color from the hardcoded geographic location and sensor level.

    Args:
        sensor_level (int): Sensor level: 0=dry, 1=low, 2=medium, 3=high.

    Returns:
        dict: {
            'alerta': str ('VERDE', 'AMARILLO', 'ROJO'),
            'riesgo_zona': str ('BAJO', 'MEDIO', 'ALTO'),
            'riesgo_score': float,
            'nivel_sensor': int,
            'coordenadas': dict
        }"""
    # Step 1: Get zone risk using hardcoded coordinates
    risk_score = get_zone_risk_score(FIXED_LATITUDE, FIXED_LONGITUDE)
    risk_level = classify_zone_risk(risk_score)

    # Step 2: Apply business rules combining zone risk and sensor level
    if risk_level == "BAJO":
        # LOW-risk zone: 0–2 → Green, 3 → Yellow
        if sensor_level <= 2:
            alert = "VERDE"
        else:
            alert = "AMARILLO"

    elif risk_level == "MEDIO":
        # MEDIUM-risk zone: 0–1 → Green, 2 → Yellow, 3 → Red
        if sensor_level <= 1:
            alert = "VERDE"
        elif sensor_level == 2:
            alert = "AMARILLO"
        else:
            alert = "ROJO"

    else:  # HIGH risk
        # HIGH-risk zone: 0 → Green, 1 → Yellow, 2–3 → Red
        if sensor_level == 0:
            alert = "VERDE"
        elif sensor_level == 1:
            alert = "AMARILLO"
        else:
            alert = "ROJO"

    return {
        "alerta": alert,
        "riesgo_zona": risk_level,
        "riesgo_score": round(risk_score, 1),
        "nivel_sensor": sensor_level,
        "coordenadas": {"latitud": FIXED_LATITUDE, "longitud": FIXED_LONGITUDE},
    }


def predict_alert_for_coordinates(latitude, longitude, sensor_level):
    """Helper function for checks using custom coordinates."""
    risk_score = get_zone_risk_score(latitude, longitude)
    risk_level = classify_zone_risk(risk_score)

    if risk_level == "BAJO":
        if sensor_level <= 2:
            alert = "VERDE"
        else:
            alert = "AMARILLO"
    elif risk_level == "MEDIO":
        if sensor_level <= 1:
            alert = "VERDE"
        elif sensor_level == 2:
            alert = "AMARILLO"
        else:
            alert = "ROJO"
    else:  # HIGH risk
        if sensor_level == 0:
            alert = "VERDE"
        elif sensor_level == 1:
            alert = "AMARILLO"
        else:
            alert = "ROJO"

    return {
        "alerta": alert,
        "riesgo_zona": risk_level,
        "riesgo_score": round(risk_score, 1),
        "nivel_sensor": sensor_level,
        "coordenadas": {"latitud": latitude, "longitud": longitude},
    }


def test_specific_coordinates():
    """Test specific coordinates and diagnose issues."""
    print("\n" + "=" * 60)
    print("🧪 MODO PRUEBA DE COORDENADAS ESPECÍFICAS")
    print("=" * 60)

    # Test coordinates
    test_coordinates = [
        (19.4326, -99.1332, "Ciudad de México (Centro)"),
        (19.5061618036, -99.1047492201, "Coordenada hardcoded del sistema"),
        (40.7128, -74.0060, "Nueva York (fuera de CDMX)"),
        (25.7617, -100.3016, "Monterrey (fuera de CDMX)"),
        (19.35, -99.35, "Límite sudoeste de CDMX"),
        (19.65, -98.95, "Límite nordeste de CDMX"),
    ]

    print("Probando diferentes coordenadas con sensor nivel 2 (medio):")
    print("-" * 60)

    for lat, lon, description in test_coordinates:
        print(f"\n📍 {description}")
        print(f"   Coordenadas: ({lat}, {lon})")

        # Check whether the location is within Mexico City
        is_in_mexico_city = is_within_mexico_city(lat, lon)
        print(f"   En CDMX: {'✅ Sí' if is_in_mexico_city else '❌ No'}")

        # Make a prediction
        try:
            result = predict_alert_for_coordinates(lat, lon, 2)
            print(f"   Riesgo zona: {result['riesgo_zona']} (score: {result['riesgo_score']})")
            print(f"   Alerta: {result['alerta']}")
        except Exception as e:
            print(f"   ❌ Error en predicción: {e}")


def main_original():
    """Original main routine for the system."""
    print("🚨 === Sistema de Predicción de Alertas de Inundación ===")
    print(f"📍 Coordenadas fijas: ({FIXED_LATITUDE}, {FIXED_LONGITUDE})")
    print("📋 Nivel sensor: 0=seco, 1=bajo, 2=medio, 3=alto")

    try:
        sensor_str = input("\n📡 Ingresa nivel del sensor (0-3): ")
        sensor_level = int(sensor_str)

        # Validate the sensor level
        if not 0 <= sensor_level <= 3:
            print("❌ Error: El nivel del sensor debe estar entre 0 y 3")
            exit(1)

        # Predict using hardcoded coordinates
        result = predict_alert(sensor_level)

        # Display the result
        print(f"\n" + "=" * 50)
        print(f"📊 RESULTADO DE LA PREDICCIÓN")
        print(f"=" * 50)
        print(
            f"📍 Coordenadas: ({result['coordenadas']['latitud']}, {result['coordenadas']['longitud']})"
        )
        print(f"📡 Nivel sensor: {sensor_level}")
        print(f"🎯 Riesgo zona: {result['riesgo_zona']} (score: {result['riesgo_score']})")

        # Display the alert with an emoji
        alert_emoji = {"VERDE": "🟢", "AMARILLO": "🟡", "ROJO": "🔴"}
        print(f"🚨 ALERTA: {alert_emoji[result['alerta']]} {result['alerta']}")

        # Explain the alert
        print(f"\n💡 Explicación:")
        if result["alerta"] == "VERDE":
            print("   ✅ Condiciones normales - No se requiere acción")
        elif result["alerta"] == "AMARILLO":
            print("   ⚠️ Precaución - Monitoreo continuo recomendado")
        else:
            print("   🚨 Peligro - Tomar medidas de seguridad inmediatas")

        # Additional checks with different levels
        print(f"\n🧪 Pruebas con diferentes niveles de sensor en esta ubicación:")
        for test_level in range(4):
            test_result = predict_alert(test_level)
            emoji = alert_emoji[test_result["alerta"]]
            print(f"   Sensor {test_level}: {emoji} {test_result['alerta']}")

        # Additional diagnostics
        print(f"\n🔍 Diagnóstico detallado:")
        print(
            f"   • Validación geográfica: {'✅ Dentro de CDMX' if is_within_mexico_city(FIXED_LATITUDE, FIXED_LONGITUDE) else '❌ Fuera de CDMX'}"
        )
        print(f"   • Rango esperado de score: 28.5 (BAJO) - 80.2 (ALTO)")
        print(f"   • Score actual: {result['riesgo_score']}")

        # Show the manual calculation
        print(f"\n🧮 Cálculo teórico del score (para referencia):")
        print(f"   • Formula: intensidad_mm * 0.6 + area_inundable_pct * 0.4")
        print(f"   • Rango intensidad: 47.5-67.0 mm")
        print(f"   • Rango área: 12.5-100.0 %")
        print(f"   • Score mínimo: 47.5*0.6 + 12.5*0.4 = {47.5 * 0.6 + 12.5 * 0.4}")
        print(f"   • Score máximo: 67.0*0.6 + 100.0*0.4 = {67.0 * 0.6 + 100.0 * 0.4}")

    except ValueError:
        print("❌ Error: El nivel del sensor debe ser un número entero entre 0 y 3.")
        exit(1)


# Add an option to run diagnostics
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_specific_coordinates()
    else:
        main_original()
