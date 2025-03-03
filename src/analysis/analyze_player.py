import pandas as pd
import os
import sys

def analyze_player(player_name):
    # Ruta del archivo consolidado
    data_folder = "data/player/consolidated/"
    file_path = os.path.join(data_folder, f"{player_name.replace(' ', '_')}.xlsx")
    
    if not os.path.exists(file_path):
        print(f"❌ Error: No se encontró el archivo {file_path}")
        return
    
    print(f"📊 Analizando datos de {player_name}...")
    
    # Cargar el archivo Excel
    xls = pd.ExcelFile(file_path)
    
    # Diccionario para almacenar estadísticas
    stats_summary = {}
    
    for sheet in xls.sheet_names:
        print(f"\n📌 Analizando sección: {sheet}")
        df = pd.read_excel(xls, sheet_name=sheet)
        
        if df.empty:
            print(f"⚠ La hoja {sheet} está vacía.")
            continue
        
        # Obtener estadísticas clave
        stats_summary[sheet] = {
            "Total Registros": len(df),
            "Promedios": df.mean(numeric_only=True).to_dict(),
            "Máximos": df.max(numeric_only=True).to_dict(),
            "Mínimos": df.min(numeric_only=True).to_dict()
        }
        
        print(df.describe())  # Mostrar estadísticas en consola
    
    print("\n✅ Análisis completado. Datos clave:")
    for section, stats in stats_summary.items():
        print(f"\n🔹 {section}:")
        print(f"   - Registros: {stats['Total Registros']}")
        print(f"   - Promedios: {stats['Promedios']}")
        print(f"   - Máximos: {stats['Máximos']}")
        print(f"   - Mínimos: {stats['Mínimos']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Uso incorrecto. Debes proporcionar el nombre del jugador.")
        print("Ejemplo: python -m src.analysis.analyze_player 'Cristian Bernardi'")
    else:
        player_name = sys.argv[1]
        analyze_player(player_name)
