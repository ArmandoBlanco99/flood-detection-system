#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagnostic script to verify the prediction correction."""

import sys
from pathlib import Path

# Add the src directory to the import path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from realtime import predict_alert_for_coordinates


def main():
    print("\n" + "=" * 70)
    print("TEST: Verificar que la coordenada problemática ahora da 39.2")
    print("=" * 70)

    # Coordinate that returned 48.4 but should return 39.2
    lat = 19.5061618036
    lon = -99.1047492201
    sensor_level = 0  # Does not affect the risk-score check

    print(f"\nCoordenadas: ({lat}, {lon})")
    print(f"Valor esperado en dataset: 39.2 (BAJO)")
    print(f"Valor que daba antes: 48.4")
    print("\nHaciendo predicción...")

    result = predict_alert_for_coordinates(lat, lon, sensor_level)

    print(f"\n" + "-" * 70)
    print("RESULTADO:")
    print("-" * 70)
    print(f"Score predicho: {result['riesgo_score']}")
    print(f"Clasificación: {result['riesgo_zona']}")
    print(f"Alerta (sensor nivel {sensor_level}): {result['alerta']}")

    # Check whether the result is correct
    if result["riesgo_score"] == 39.2:
        print("\n✅ CORRECTO - El problema ha sido SOLUCIONADO")
    else:
        print(f"\n⚠️ Valor inesperado: {result['riesgo_score']} (esperado 39.2)")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
