import pandas as pd
import os
import sys
from PIL import Image, ImageDraw, ImageFont

# 📌 Directorios
DATA_FOLDER = "data/player/consolidated/"
VISUALS_FOLDER = "data/player/visuals/"
FONTS_FOLDER = "src/fonts/"
PLAYER_IMAGES_FOLDER = "data/player/visuals/"
HEATMAP_IMAGES_FOLDER = "data/player/visuals/"

# 📌 Traducción de las categorías
STAT_TRANSLATIONS = {
    "Goals": "Goles",
    "Goals per game": "Goles por partido",
    "Shots per game": "Tiros por partido",
    "Shots on target per game": "Tiros al arco por partido",
    "Goal conversion": "Efectividad de gol",
    "Penalty goals": "Goles de penal",
    "Penalty conversion": "Efectividad en penales",
    "Assists": "Asistencias",
    "Key passes per game": "Pases clave por partido",
    "Accurate per game": "Pases precisos por partido",
    "Acc. long balls": "Pases largos precisos",
    "Acc. crosses": "Centros precisos",
    "Balls recovered per game": "Balones recuperados por partido",
    "Dribbled past per game": "Veces regateado por partido",
    "Clearances per game": "Despejes por partido",
    "Errors leading to shot": "Errores que generaron tiros",
    "Succ. dribbles": "Regates exitosos",
    "Total duels won": "Duelos ganados",
    "Aerial duels won": "Duelos aéreos ganados",
    "Fouls": "Faltas cometidas",
    "Was fouled": "Faltas recibidas",
    "Offsides": "Fuera de juego",
    "Yellow": "Tarjetas amarillas",
    "Yellow-Red": "Doble amarilla",
    "Red cards": "Tarjetas rojas"
}

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
                translated_stats = {
                    STAT_TRANSLATIONS.get(stat, stat): value for stat, value in df.set_index("Estadística")["Valor"].to_dict().items()
                }
                stats[sheet] = translated_stats
    return stats

# 📌 Crear imagen de la ficha del jugador
def create_player_card(player_name):
    xls = load_player_data(player_name)
    if xls is None:
        return

    player_info = extract_player_info(xls)
    player_stats = extract_player_stats(xls)

    # 📌 Configurar imagen
    img_width, img_height = 800, 1100
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

    # 📌 Cargar imagen del jugador si existe
    player_image_path = os.path.join(PLAYER_IMAGES_FOLDER, f"{player_name.replace(' ', '_')}.png")
    if os.path.exists(player_image_path):
        player_img = Image.open(player_image_path).resize((120, 120))
        img.paste(player_img, (20, 20))

    # 📌 Posiciones iniciales
    x_text = 160
    y_position = 40

    # 📌 Título
    draw.text((x_text, y_position), player_info["Nombre"], fill="black", font=font_title)
    y_position += 50

    # 📌 Datos generales
    for key, value in player_info.items():
        if key != "Nombre":
            draw.text((x_text, y_position), f"{key}: {value}", fill="black", font=font_subtitle)
            y_position += 40

    y_position += 30

    # 📌 Estadísticas clave en dos columnas
    column1_x = 20
    column2_x = 400
    max_stats_per_column = 8
    col_count = 0

    for category, stats in player_stats.items():
        if col_count % 2 == 0:
            x_col = column1_x
        else:
            x_col = column2_x

        draw.text((x_col, y_position), f"{category.upper()}:", fill="black", font=font_subtitle)
        y_position += 30
        for stat, value in stats.items():
            draw.text((x_col + 10, y_position), f"- {stat}: {value}", fill="black", font=font_text)
            y_position += 30

        y_position += 20
        col_count += 1
        if col_count == max_stats_per_column:
            y_position = 280

    # 📌 Agregar mapa de calor
    heatmap_path = os.path.join(HEATMAP_IMAGES_FOLDER, f"heatmap_{player_name.replace(' ', '_')}.png")
    if os.path.exists(heatmap_path):
        heatmap_img = Image.open(heatmap_path).resize((300, 150))
        img.paste(heatmap_img, (250, img_height - 200))

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


# python -m src.visualization.generate_player_card 'Cristian Bernardi'