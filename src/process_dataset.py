import pandas as pd
import numpy as np

# Map string ranges to numeric values
intensity_map = {
    "41 a 54": 47.5,  # LOW RISK
    "54 a 60": 57.0,  # LOW–MEDIUM RISK
    "60 a 64": 62.0,  # MEDIUM–HIGH RISK
    "64 a 70": 67.0,  # HIGH RISK
}

area_map = {
    "0 a 25": 12.5,  # VERY LOW RISK
    "26 a 49": 37.5,  # LOW RISK
    "50 a 72": 61.0,  # MEDIUM RISK
    "73 a 99": 86.0,  # HIGH RISK
    "100": 100.0,  # VERY HIGH RISK
}


def process_dataset():
    print("🔄 Cargando dataset original...")

    # Load the dataset with the correct encoding
    df = pd.read_csv("Dataset - Full(Dataset).csv", encoding="latin-1")

    print(f"✅ Dataset cargado: {len(df)} filas")
    print(f"📊 Columnas originales: {list(df.columns)}")

    # Split coordinates into latitude and longitude
    print("\n🗺️ Procesando coordenadas...")
    coords = df["coordinates"].str.strip('"').str.split(",", expand=True)
    df["latitud"] = coords[0].astype(float)
    df["longitud"] = coords[1].astype(float)

    # Convert rainfall intensity
    print("🌧️ Procesando intensidad de precipitación...")
    df["intensidad_mm"] = df["intens_mm"].map(intensity_map)

    # Convert the floodable-area percentage
    print("💧 Procesando porcentaje de área inundable...")
    df["area_inundable_pct"] = df["%_área"].map(area_map)

    # Create a combined risk score using a weighted average
    # Intensity has greater weight (60%) than area (40%)
    df["riesgo_zona_score"] = df["intensidad_mm"] * 0.6 + df["area_inundable_pct"] * 0.4

    # Classify the zone risk level using its score
    def classify_zone(score):
        if score <= 45:
            return "BAJO"
        elif score <= 65:
            return "MEDIO"
        else:
            return "ALTO"

    df["nivel_riesgo_zona"] = df["riesgo_zona_score"].apply(classify_zone)

    # Create the processed dataset with relevant columns
    processed_df = df[
        [
            "latitud",
            "longitud",
            "intensidad_mm",
            "area_inundable_pct",
            "riesgo_zona_score",
            "nivel_riesgo_zona",
        ]
    ].copy()

    # Remove duplicates to optimize the dataset
    processed_df = processed_df.drop_duplicates()

    print(f"\n📈 Dataset procesado:")
    print(f"   • Filas después de eliminar duplicados: {len(processed_df)}")
    print(
        f"   • Rango de intensidad: {processed_df['intensidad_mm'].min():.1f} - {processed_df['intensidad_mm'].max():.1f} mm"
    )
    print(
        f"   • Rango de área inundable: {processed_df['area_inundable_pct'].min():.1f} - {processed_df['area_inundable_pct'].max():.1f} %"
    )
    print(
        f"   • Rango de score de riesgo: {processed_df['riesgo_zona_score'].min():.1f} - {processed_df['riesgo_zona_score'].max():.1f}"
    )

    print(f"\n🎯 Distribución por nivel de riesgo:")
    print(processed_df["nivel_riesgo_zona"].value_counts())

    # Save the processed dataset
    output_file = "processed_dataset.csv"
    processed_df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"\n💾 Dataset procesado guardado como: {output_file}")

    # Display a sample of the processed dataset
    print(f"\n📋 Primeras 5 filas del dataset procesado:")
    print(processed_df.head())

    return processed_df


if __name__ == "__main__":
    processed_dataset = process_dataset()
