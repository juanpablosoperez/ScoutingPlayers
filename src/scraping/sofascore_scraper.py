from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

# Configuración del WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ejecutar en segundo plano
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--no-sandbox")

webdriver_path = "src/scraping/chromedriver.exe"
service = Service(webdriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL de la Primera Nacional en SofaScore
url = "https://www.sofascore.com/tournament/football/argentina/primera-nacional/703#id:71009,tab:details"
driver.get(url)

# Esperar a que la página cargue completamente
time.sleep(5)

# Scroll down para cargar más jugadores dinámicamente
body = driver.find_element(By.TAG_NAME, "body")
for _ in range(7):  # Más scrolls para asegurarnos de obtener todos los jugadores
    body.send_keys(Keys.PAGE_DOWN)
    time.sleep(1)

# Extraer nombres de jugadores desde los links que contienen "/player/"
try:
    jugadores = driver.find_elements(By.XPATH, "//a[contains(@href, '/player/')]")

    datos_jugadores = []
    for jugador in jugadores:
        nombre = jugador.text.strip()
        if nombre and nombre not in datos_jugadores:  # Evitar duplicados
            datos_jugadores.append({"Nombre": nombre})

    # Convertir a DataFrame y guardar en CSV
    df = pd.DataFrame(datos_jugadores)
    df.to_csv("data/jugadores_primera_nacional.csv", index=False, encoding="utf-8")

    print(f"✅ Scraping completado. {len(datos_jugadores)} jugadores guardados en 'data/jugadores_primera_nacional.csv'.")

except Exception as e:
    print(f"❌ Error al extraer datos: {e}")

# Cerrar el navegador
driver.quit()
