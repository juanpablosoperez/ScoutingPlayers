import pandas as pd
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from math import pi

# 📌 Ruta donde se encuentran los datos de los jugadores
DATA_FOLDER = "data/player/consolidated/"
VISUALS_FOLDER = "data/player/visuals/"

# 📌 Función para cargar los datos del jugador
def load_player_data(player_name):
    file_path = os.path.join(DATA_FOLDER, f"{player_name.replace(' ', '_')}.xlsx")
    if not os.path.exists(file_path):
        print(f"❌ Error: No se encontró el archivo {file_path}")
        return None
    return pd.ExcelFile(file_path)

# 📌 Función para limpiar valores numéricos de texto como "3.7 (73%)"
def clean_numeric(value):
    if isinstance(value, str):
        try:
            return float(value.split()[0])
        except ValueError:
            return np.nan  # Si no se puede convertir, se asigna NaN
    return value

# 📌 Función para generar gráfico de barras
def plot_bar_chart(df, player_name, section):
    plt.figure(figsize=(10, 6))
    sns.barplot(x=df['Estadística'], y=df['Valor'], palette="viridis")
    plt.xticks(rotation=45, ha='right')
    plt.title(f"{section} - {player_name}")
    plt.ylabel("Valor")
    plt.xlabel("Estadística")
    plt.tight_layout()
    
    # Guardar imagen
    file_path = os.path.join(VISUALS_FOLDER, f"{player_name.replace(' ', '_')}_{section}_barras.png")
    plt.savefig(file_path)
    plt.show()

# 📌 Función para generar radar chart (Spider Chart)
def plot_radar_chart(df, player_name, section):
    categories = df['Estadística'].tolist()
    values = df['Valor'].tolist()
    values += values[:1]  # Cerrar el círculo en el gráfico
    
    angles = [n / float(len(categories)) * 2 * pi for n in range(len(categories))]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color='blue', alpha=0.3)
    ax.plot(angles, values, color='blue', linewidth=2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12)
    ax.set_yticklabels([])
    ax.set_title(f"{section} - {player_name}", size=14)

    # Guardar imagen
    file_path = os.path.join(VISUALS_FOLDER, f"{player_name.replace(' ', '_')}_{section}_radar.png")
    plt.savefig(file_path)
    plt.show()

# 📌 Función para gráfico de líneas (Evolución)
def plot_line_chart(df, player_name, section):
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x=df.index, y='Valor', marker='o', linewidth=2.5)
    plt.title(f"Evolución de {section} - {player_name}")
    plt.xlabel("Partido")
    plt.ylabel("Valor")
    plt.grid(True)
    plt.tight_layout()

    # Guardar imagen
    file_path = os.path.join(VISUALS_FOLDER, f"{player_name.replace(' ', '_')}_{section}_lineas.png")
    plt.savefig(file_path)
    plt.show()

# 📌 Función principal para visualizar los datos del jugador
def visualize_player(player_name):
    xls = load_player_data(player_name)
    if xls is None:
        return
    
    os.makedirs(VISUALS_FOLDER, exist_ok=True)
    
    # 📌 Extraer y mostrar información del jugador (Resumen)
    if "Resumen" in xls.sheet_names:
        df_resumen = pd.read_excel(xls, sheet_name="Resumen")
        if not df_resumen.empty:
            resumen_dict = df_resumen.iloc[0].to_dict()
            print("\n📌 **Datos Generales del Jugador:**")
            for key, value in resumen_dict.items():
                print(f"   - {key}: {value}")

    # 📌 Generar gráficos para cada sección relevante
    for section in ["Attacking", "Passing", "Defending", "Other (per game)"]:
        if section in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=section)
            if "Estadística" in df.columns and "Valor" in df.columns:
                df["Valor"] = df["Valor"].apply(clean_numeric)

                print(f"\n📊 Generando gráficos para {section} de {player_name}...")
                plot_bar_chart(df, player_name, section)
                plot_radar_chart(df, player_name, section)
                plot_line_chart(df, player_name, section)

    print(f"\n✅ Gráficos generados y guardados en '{VISUALS_FOLDER}'.")

# 📌 Ejecutar script desde la línea de comandos
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Uso incorrecto. Debes proporcionar el nombre del jugador.")
        print("Ejemplo: python -m src.visualization.visualize_player 'Cristian Bernardi'")
    else:
        player_name = sys.argv[1]
        visualize_player(player_name)
