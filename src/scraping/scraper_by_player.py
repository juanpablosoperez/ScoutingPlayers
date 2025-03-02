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

# URL de la B Nacional en Sofascore
url_base = "https://www.sofascore.com/tournament/football/argentina/primera-nacional/703#id:71009,tab:details"
driver.get(url_base)
time.sleep(5)  # Esperamos que cargue la página

# 📌 Obtener la lista de jugadores
jugadores = driver.find_elements(By.XPATH, "//table//tr/td//a")

if not jugadores:
    print("❌ No se encontraron jugadores en la página.")
    driver.quit()
    exit()

# 📋 Mostrar la lista de jugadores disponibles
print("\n📋 Lista de jugadores disponibles:")
jugadores_dict = {}
for i, jugador in enumerate(jugadores, start=1):
    nombre_jugador = jugador.text.strip()
    jugadores_dict[nombre_jugador.lower()] = jugador
    print(f"{i}. {nombre_jugador}")

# 🎯 Pedir al usuario que elija un jugador
jugador_buscado = input("\nIngrese el nombre exacto del jugador a analizar: ").strip().lower()

# Validar si el jugador existe
if jugador_buscado in jugadores_dict:
    jugador_seleccionado = jugadores_dict[jugador_buscado]
    jugador_nombre = jugador_seleccionado.text
    print(f"📊 Analizando a {jugador_nombre}...")
    jugador_seleccionado.click()
    time.sleep(5)  # Esperamos a que cargue la página del jugador
else:
    print(f"❌ Jugador '{jugador_buscado}' no encontrado en la lista.")
    driver.quit()
    exit()

# 📌 Extraer información del jugador
datos_jugador = {"Nombre": jugador_nombre}

try:
    datos_jugador["Equipo"] = driver.find_element(By.XPATH, "//div[@data-testid='player_info']//a").text
    datos_jugador["Edad"] = driver.find_element(By.XPATH, "//div[contains(text(),'yrs')]").text
    datos_jugador["Altura"] = driver.find_element(By.XPATH, "//div[contains(text(),'cm')]").text
    datos_jugador["Pie Preferido"] = driver.find_element(By.XPATH, "//div[contains(text(),'Right') or contains(text(),'Left')]").text
    datos_jugador["Valor de Mercado"] = driver.find_element(By.XPATH, "//div[contains(text(),'€')]").text
except:
    print("⚠ No se pudo obtener toda la información básica.")

# 🔍 Extraer estadísticas por categoría
categorias = {
    "Resumen": "summary",
    "Ataque": "attack",
    "Pases": "passing",
    "Defensa": "defence",
    "Otros": "other",
    "Tarjetas": "cards"
}

for categoria, tab_id in categorias.items():
    try:
        boton_categoria = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[@data-tabid='{tab_id}']"))
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

# 📁 Guardar en CSV
df = pd.DataFrame([datos_jugador])
csv_filename = f"data/detalles_{jugador_nombre.replace(' ', '_')}.csv"
df.to_csv(csv_filename, index=False, encoding='utf-8')

print(f"✅ Datos de {jugador_nombre} guardados en '{csv_filename}'")

driver.quit()
print("🎉 Scraping finalizado.")
