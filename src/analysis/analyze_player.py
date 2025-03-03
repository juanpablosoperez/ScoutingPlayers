import pandas as pd
import os
import sys
import numpy as np

def clean_numeric(value):
    """Convierte valores como '3.7 (73%)' en números, eliminando texto innecesario."""
    if isinstance(value, str):
        value = value.split()[0]  # Tomar solo el primer valor antes del paréntesis
    try:
        return float(value)
    except ValueError:
        return np.nan  # Si no se puede convertir, asignar NaN

def analyze_player(player_name):
    # Ruta del archivo consolidado
    data_folder = "data/player/consolidated/"
    file_path = os.path.join(data_folder, f"{player_name.replace(' ', '_')}.xlsx")
    
    if not os.path.exists(file_path):
        print(f"❌ Error: No se encontró el archivo {file_path}")
        return
    
    print(f"\n📊 Analizando datos de {player_name}...\n")

    # Cargar el archivo Excel
    xls = pd.ExcelFile(file_path)
    
    # Diccionario para almacenar estadísticas
    stats_summary = {}

    # 📌 **Extraer datos de la hoja "Resumen"**
    if "Resumen" in xls.sheet_names:
        df_resumen = pd.read_excel(xls, sheet_name="Resumen")

        if not df_resumen.empty:
            print("📌 **Datos Generales del Jugador:**")
            resumen_dict = df_resumen.iloc[0].to_dict()

            jugador_info = {
                "Nombre": resumen_dict.get("Nombre", "No disponible"),
                "Equipo": resumen_dict.get("Equipo", "No disponible"),
                "Edad": resumen_dict.get("Edad", "No disponible"),
                "Altura": resumen_dict.get("Altura", "No disponible"),
                "Pie Preferido": resumen_dict.get("Pie Preferido", "No disponible"),
                "Valor de Mercado": resumen_dict.get("Valor de Mercado", "No disponible")
            }

            for key, value in jugador_info.items():
                print(f"   - {key}: {value}")

    # 📌 **Analizar estadísticas de cada hoja**
    for sheet in xls.sheet_names:
        if sheet in ["Resumen", "Mapa de Calor"]:  # Omitir hojas no analizables
            continue

        print(f"\n📌 **Analizando sección: {sheet}**")
        df = pd.read_excel(xls, sheet_name=sheet)
        
        if df.empty:
            print(f"⚠ La hoja {sheet} está vacía.")
            continue

        # Si las columnas son "Estadística" y "Valor", mostrar correctamente
        if "Estadística" in df.columns and "Valor" in df.columns:
            print("\n📊 **Datos Detallados:**")
            for _, row in df.iterrows():
                print(f"   - {row['Estadística']}: {row['Valor']}")

            # Convertir valores a numéricos para estadísticas
            df["Valor"] = df["Valor"].apply(clean_numeric)

        # Obtener estadísticas clave
        stats_summary[sheet] = {
            "Total Registros": len(df),
            "Promedios": df.mean(numeric_only=True).to_dict(),
            "Máximos": df.max(numeric_only=True).to_dict(),
            "Mínimos": df.min(numeric_only=True).to_dict()
        }

    # 📋 **Resumen final**
    print("\n✅ **Análisis completado. Datos clave:**")
    for section, stats in stats_summary.items():
        print(f"\n🔹 **{section}:**")
        print(f"   - Registros: {stats['Total Registros']}")
        print(f"   - Promedios:")
        for key, value in stats["Promedios"].items():
            print(f"     - {key}: {value}")
        print(f"   - Máximos:")
        for key, value in stats["Máximos"].items():
            print(f"     - {key}: {value}")
        print(f"   - Mínimos:")
        for key, value in stats["Mínimos"].items():
            print(f"     - {key}: {value}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Uso incorrecto. Debes proporcionar el nombre del jugador.")
        print("Ejemplo: python -m src.analysis.analyze_player 'Cristian Bernardi'")
    else:
        player_name = sys.argv[1]
        analyze_player(player_name)
