from flask import Flask, request, render_template, jsonify
from realtime import (
    predict_alert_for_coordinates,
    is_within_mexico_city,
    FIXED_LATITUDE,
    FIXED_LONGITUDE,
)
import logging
from pathlib import Path
import json

app = Flask(__name__, template_folder="templates", static_folder="static")

# Configure logging for readable terminal output
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
app.logger.setLevel(logging.INFO)

# Directory and configuration file for persistent coordinates
script_dir = Path(__file__).resolve().parent
_coords_config_file = script_dir / "coords_config.json"

# Current coordinates, initialized from realtime defaults
current_coordinates = {"latitud": FIXED_LATITUDE, "longitud": FIXED_LONGITUDE}

# Try to load persisted coordinates if available
try:
    if _coords_config_file.exists():
        with open(_coords_config_file, "r", encoding="utf-8") as _f:
            data = json.load(_f)
            if "latitud" in data and "longitud" in data:
                current_coordinates["latitud"] = float(data["latitud"])
                current_coordinates["longitud"] = float(data["longitud"])
                app.logger.info(f"📍 Coordenadas cargadas desde {_coords_config_file}")
except Exception as _e:
    app.logger.warning(f"No se pudieron cargar coordenadas guardadas: {_e}")

# Global variable storing the latest prediction result
latest_result = None


@app.route("/ingest", methods=["POST"])
def ingest():
    global latest_result
    data = request.get_json(force=True, silent=True) or {}
    v = data.get("v")
    pct = data.get("pct")

    if isinstance(v, (int, float)) and isinstance(pct, (int, float)):
        app.logger.info(f"v={v:.3f} V | pct={pct:.2f} %")

        # Map voltage to sensor level (0–3)
        if v <= 0.695:
            sensor_level = 0
        elif v <= 0.759:
            sensor_level = 1
        elif v <= 0.812:
            sensor_level = 2
        else:
            sensor_level = 3

        # Predict using the currently saved coordinates
        result = predict_alert_for_coordinates(
            current_coordinates["latitud"], current_coordinates["longitud"], sensor_level
        )
        latest_result = result

        app.logger.info(f"🚨 Nivel sensor: {sensor_level} → Alerta: {result['alerta']}")
        app.logger.info(f"Detalles de la predicción: {result}")

    else:
        app.logger.info(f"Datos recibidos inválidos o vacíos: {data}")

    return {"ok": True}


@app.route("/", methods=["GET"])
def index():
    """Serve the main web page."""
    return render_template("index.html")


@app.route("/api/status", methods=["GET"])
def get_status():
    """Return the latest prediction status through the API."""
    if latest_result is None:
        return jsonify(
            {
                "alerta": "GRIS",
                "riesgo_zona": "DESCONOCIDO",
                "riesgo_score": 0,
                "nivel_sensor": -1,
                "coordenadas": current_coordinates,
                "mensaje": "Esperando datos del sensor...",
            }
        )
    return jsonify(latest_result)


@app.route("/api/coords", methods=["GET"])
def api_get_coords():
    """Return the currently configured coordinates."""
    return jsonify(current_coordinates)


@app.route("/api/coords", methods=["POST"])
def api_set_coords():
    """Set coordinates through the web interface and save them to disk."""
    global current_coordinates
    data = request.get_json(force=True, silent=True) or {}
    lat = data.get("lat")
    lon = data.get("lon")
    try:
        lat = float(lat)
        lon = float(lon)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "lat y lon deben ser números"}), 400

    current_coordinates["latitud"] = lat
    current_coordinates["longitud"] = lon

    # Persist the configuration
    try:
        with open(_coords_config_file, "w", encoding="utf-8") as _f:
            json.dump(current_coordinates, _f)
    except Exception as e:
        app.logger.warning(f"No se pudo guardar coordenadas: {e}")

    # Log geographic validation, optionally
    if not is_within_mexico_city(lat, lon):
        app.logger.warning(f"⚠️ Coordenadas fuera de rango CDMX: ({lat}, {lon})")

    app.logger.info(f"📍 Coordenadas actualizadas → {current_coordinates}")
    return jsonify({"ok": True, "coordenadas": current_coordinates})


if __name__ == "__main__":
    import os

    # Detect the environment: development or production
    debug_mode = os.environ.get("FLASK_ENV", "development") == "development"

    if debug_mode:
        app.logger.info("🔧 MODO DESARROLLO - Iniciando servidor Flask...")
        app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
    else:
        app.logger.info("🚀 MODO PRODUCCIÓN - Iniciando servidor Flask...")
        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
