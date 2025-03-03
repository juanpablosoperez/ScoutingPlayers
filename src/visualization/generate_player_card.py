import pandas as pd
import os
import sys
from PIL import Image, ImageDraw, ImageFont

# 📌 Ruta donde se encuentran los datos consolidados y visuales
DATA_FOLDER = "data/player/consolidated/"
VISUALS_FOLDER = "data/player/visuals/"
FONTS_FOLDER = "src/fonts/"

# 📌 Cargar datos del jugador
def load_player_data(player_name):
    file_path = os.path.join(DATA_FOLDER, f"{player_name.replace(' ', '_')}.xlsx")
    if not os.path.exists(file_path):
        print(f"❌ Error: No se encontró el archivo {file_path}")
        return None
    return pd.ExcelFile(file_path)

# 📌 Extraer la información clave del jugador
def extract_player_info(xls):
    player_info = {}
    
    if "Resumen" in xls.sheet_names:
        df_resumen = pd.read_excel(xls, sheet_name="Resumen")
        if not df_resumen.empty:
            resumen_dict = df_resumen.iloc[0].to_dict()
            player_info = {
                "Nombre": resumen_dict.get("Nombre", "No disponible"),
                "Equipo": resumen_dict.get("Equipo", "No disponible"),
                "Edad": resumen_dict.get("Edad", "No disponible"),
                "Altura": resumen_dict.get("Altura", "No disponible"),
                "Pie Preferido": resumen_dict.get("Pie Preferido", "No disponible"),
                "Valor de Mercado": resumen_dict.get("Valor de Mercado", "No disponible"),
            }
    return player_info

# 📌 Extraer estadísticas clave del jugador
def extract_player_stats(xls):
    stats = {}
    for sheet in ["Attacking", "Passing", "Defending", "Other (per game)", "Cards"]:
        if sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)
            if "Estadística" in df.columns and "Valor" in df.columns:
                stats[sheet] = df.set_index("Estadística")["Valor"].to_dict()
    return stats

# 📌 Crear imagen de la ficha del jugador
def create_player_card(player_name):
    xls = load_player_data(player_name)
    if xls is None:
        return

    player_info = extract_player_info(xls)
    player_stats = extract_player_stats(xls)

    # 📌 Configurar imagen
    img_width, img_height = 600, 800
    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)
    
    # 📌 Cargar fuente
    try:
        font_title = ImageFont.truetype(os.path.join(FONTS_FOLDER, "arial_bold.ttf"), 40)
        font_subtitle = ImageFont.truetype(os.path.join(FONTS_FOLDER, "arial.ttf"), 30)
        font_text = ImageFont.truetype(os.path.join(FONTS_FOLDER, "arial.ttf"), 25)
    except:
        print("⚠ No se encontró la fuente, usando predeterminada.")
        font_title = font_subtitle = font_text = ImageFont.load_default()

    # 📌 Posiciones iniciales
    y_position = 20

    # 📌 Título
    draw.text((20, y_position), player_info["Nombre"], fill="black", font=font_title)
    y_position += 50

    # 📌 Datos generales
    draw.text((20, y_position), f"Equipo: {player_info['Equipo']}", fill="black", font=font_subtitle)
    y_position += 40
    draw.text((20, y_position), f"Edad: {player_info['Edad']}", fill="black", font=font_subtitle)
    y_position += 40
    draw.text((20, y_position), f"Altura: {player_info['Altura']}", fill="black", font=font_subtitle)
    y_position += 40
    draw.text((20, y_position), f"Pie Preferido: {player_info['Pie Preferido']}", fill="black", font=font_subtitle)
    y_position += 40
    draw.text((20, y_position), f"Valor de Mercado: {player_info['Valor de Mercado']}", fill="black", font=font_subtitle)
    y_position += 60

    # 📌 Estadísticas clave
    for category, stats in player_stats.items():
        draw.text((20, y_position), f"{category.upper()}:", fill="black", font=font_subtitle)
        y_position += 30
        for stat, value in stats.items():
            draw.text((30, y_position), f"- {stat}: {value}", fill="black", font=font_text)
            y_position += 30
        y_position += 20

    # 📌 Guardar imagen
    os.makedirs(VISUALS_FOLDER, exist_ok=True)
    output_path = os.path.join(VISUALS_FOLDER, f"{player_name.replace(' ', '_')}_ficha.png")
    img.save(output_path)

    print(f"✅ Ficha del jugador generada: {output_path}")

# 📌 Ejecutar script desde la línea de comandos
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Uso incorrecto. Debes proporcionar el nombre del jugador.")
        print("Ejemplo: python -m src.visualization.generate_player_card 'Cristian Bernardi'")
    else:
        player_name = sys.argv[1]
        create_player_card(player_name)
