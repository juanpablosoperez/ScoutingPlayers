from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Configuración del WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=options)

# URL base de la B Nacional en Sofascore
url_base = "https://www.sofascore.com/tournament/football/argentina/primera-nacional/703#id:71009,tab:details"
driver.get(url_base)
time.sleep(5)  # Esperar carga inicial

# 📌 Scrapeo de todas las páginas de jugadores
jugadores_dict = {}
pagina_actual = 1

while True:
    print(f"📄 Scrapeando página {pagina_actual}...")

    jugadores = driver.find_elements(By.XPATH, "//table//tr/td//a")

    for jugador in jugadores:
        nombre_jugador = jugador.text.strip()
        if nombre_jugador:
            jugadores_dict[nombre_jugador.lower()] = jugador

    # Buscar botón para pasar a la siguiente página
    try:
        siguiente_pagina = driver.find_element(By.XPATH, "//button[@aria-label='Next page']")
        driver.execute_script("arguments[0].click();", siguiente_pagina)
        time.sleep(5)
        pagina_actual += 1
    except:
        print("📌 No hay más páginas.")
        break  # No hay más páginas, salimos del loop

# 📋 Mostrar la lista de jugadores disponibles
print("\n📋 Lista de jugadores disponibles:")
for i, nombre in enumerate(jugadores_dict.keys(), start=1):
    print(f"{i}. {nombre.title()}")

# 🎯 Pedir al usuario que seleccione un jugador
jugador_buscado = input("\nIngrese el nombre exacto del jugador a analizar: ").strip().lower()

# Verificar si el jugador existe en la lista
if jugador_buscado in jugadores_dict:
    jugador_seleccionado = jugadores_dict[jugador_buscado]
    jugador_nombre = jugador_seleccionado.text
    print(f"📊 Analizando a {jugador_nombre}...")
    jugador_seleccionado.click()
    time.sleep(5)
else:
    print(f"❌ Jugador '{jugador_buscado}' no encontrado en la lista.")
    driver.quit()
    exit()

# 📌 Extraer información general del jugador
datos_jugador = {"Nombre": jugador_nombre}

try:
    datos_jugador["Equipo"] = driver.find_element(By.XPATH, "//div[@data-testid='player_info']//a").text
    datos_jugador["Edad"] = driver.find_element(By.XPATH, "//div[contains(text(),'yrs')]").text
    datos_jugador["Altura"] = driver.find_element(By.XPATH, "//div[contains(text(),'cm')]").text
    datos_jugador["Pie Preferido"] = driver.find_element(By.XPATH, "//div[contains(text(),'Right') or contains(text(),'Left')]").text
    datos_jugador["Valor de Mercado"] = driver.find_element(By.XPATH, "//div[contains(text(),'€')]").text
except:
    print("⚠ No se pudo obtener toda la información básica.")

# 🔥 Extraer Sofascore Rating
try:
    rating = driver.find_element(By.XPATH, "//span[@role='meter']").text
    datos_jugador["Rating Sofascore"] = rating
except:
    print("⚠ No se pudo obtener el rating del jugador.")

# 🔍 Extraer estadísticas detalladas
categorias = ["Matches", "Attacking", "Passing", "Defending", "Other (per game)", "Cards"]

for categoria in categorias:
    try:
        boton_categoria = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[span[contains(text(),'{categoria}')]]"))
        )
        driver.execute_script("arguments[0].click();", boton_categoria)
        time.sleep(3)

        estadisticas = driver.find_elements(By.XPATH, "//div[@class='Box fTPNOD']//div[@class='Box Flex dlyXLO bnpRyo']")
        for estadistica in estadisticas:
            try:
                key = estadistica.find_element(By.XPATH, "./span[1]").text
                value = estadistica.find_element(By.XPATH, "./span[2]").text
                datos_jugador[f"{categoria} - {key}"] = value
            except:
                continue
    except:
        print(f"⚠ No se pudo obtener datos de {categoria}")

# 🔄 Extraer historial de temporadas y equipos
try:
    temporadas = driver.find_elements(By.XPATH, "//span[@color='onSurface.nLv1']")
    equipos = driver.find_elements(By.XPATH, "//img[contains(@src, 'team')]")

    historial = []
    for i in range(len(temporadas)):
        try:
            temporada = temporadas[i].text
            equipo = equipos[i].get_attribute("alt")
            historial.append(f"{temporada}: {equipo}")
        except:
            continue

    datos_jugador["Historial de Temporadas"] = " | ".join(historial)
except:
    print("⚠ No se pudo obtener el historial de temporadas.")

# 📁 Guardar en CSV
df = pd.DataFrame([datos_jugador])
csv_filename = f"data/detalles_{jugador_nombre.replace(' ', '_')}.csv"
df.to_csv(csv_filename, index=False, encoding='utf-8')

print(f"✅ Datos de {jugador_nombre} guardados en '{csv_filename}'")

driver.quit()
print("🎉 Scraping finalizado.")
