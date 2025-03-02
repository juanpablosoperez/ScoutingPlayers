from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import sys

# Recibir el nombre del jugador como argumento
if len(sys.argv) < 2:
    print("❌ Debes proporcionar el nombre del jugador.")
    sys.exit(1)

jugador_buscado = sys.argv[1]
print(f"📊 Analizando a {jugador_buscado}...")

# Configurar Selenium con opciones avanzadas
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-extensions")  
chrome_options.add_argument("--disable-dev-shm-usage")  
chrome_options.add_argument("--disable-software-rasterizer")  

# Ruta al ChromeDriver
service = Service("src/scraping/chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL de Sofascore (ajusta según tu liga)
url_base = "https://www.sofascore.com/tournament/football/argentina/primera-nacional/703#id:71009,tab:details"
driver.get(url_base)

# Esperar que la página cargue completamente
wait = WebDriverWait(driver, 15)
time.sleep(5)  # Espera inicial

# 🔄 Buscar el jugador DESDE LA ÚLTIMA PÁGINA HACIA ATRÁS
pagina_actual = 41  # Última página
encontrado = False

while pagina_actual > 0:
    print(f"🔎 Buscando en página {pagina_actual}...")

    try:
        # Esperar a que la tabla cargue
        tabla = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "kLmlmP")))
        filas = tabla.find_elements(By.TAG_NAME, "tr")

        for fila in filas:
            columnas = fila.find_elements(By.TAG_NAME, "td")
            if len(columnas) >= 3:
                nombre = columnas[2].text.strip()
                if nombre == jugador_buscado:
                    print(f"✅ Jugador {jugador_buscado} encontrado. Obteniendo su URL...")

                    # Buscar el enlace correcto dentro de la fila
                    enlaces = fila.find_elements(By.TAG_NAME, "a")
                    url_jugador = None
                    for enlace in enlaces:
                        url_relativa = enlace.get_attribute("href")
                        if "/player/" in url_relativa:  # Asegurarnos de que es la URL de un jugador
                            url_jugador = url_relativa  # La URL ya es completa
                            break
                    
                    if not url_jugador:
                        print("❌ No se pudo obtener la URL del jugador.")
                        driver.quit()
                        sys.exit(1)

                    print(f"🔗 URL del perfil: {url_jugador}")

                    # Acceder a la página del jugador
                    driver.get(url_jugador)
                    time.sleep(5)  # Esperar carga del perfil
                    encontrado = True
                    break

        if encontrado:
            break  # Salir del bucle si el jugador fue encontrado

        # Ir a la página anterior
        try:
            boton_anterior = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@class="Button llwjsV" and not(@disabled)]')))
            driver.execute_script("arguments[0].click();", boton_anterior)
            time.sleep(4)
        except Exception:
            print("⚠ No se encontró el botón de página anterior. Fin del retroceso.")
            break

    except Exception as e:
        print(f"❌ Error buscando al jugador: {e}")
        break

if not encontrado:
    print(f"❌ No se encontró a {jugador_buscado}.")
    driver.quit()
    sys.exit(1)

# 📌 Extraer información del jugador
datos_jugador = {"Nombre": jugador_buscado}

try:
    datos_jugador["Equipo"] = driver.find_element(By.XPATH, "//div[@data-testid='player_info']//a").text
except:
    datos_jugador["Equipo"] = "No disponible"

try:
    datos_jugador["Edad"] = driver.find_element(By.XPATH, "//div[contains(text(),'yrs')]").text
except:
    datos_jugador["Edad"] = "No disponible"

try:
    datos_jugador["Altura"] = driver.find_element(By.XPATH, "//div[contains(text(),'cm')]").text
except:
    datos_jugador["Altura"] = "No disponible"

try:
    datos_jugador["Pie Preferido"] = driver.find_element(By.XPATH, "//div[contains(text(),'Right') or contains(text(),'Left')]").text
except:
    datos_jugador["Pie Preferido"] = "No disponible"

try:
    datos_jugador["Valor de Mercado"] = driver.find_element(By.XPATH, "//div[contains(text(),'€')]").text
except:
    datos_jugador["Valor de Mercado"] = "No disponible"

# 📁 Guardar en CSV
df_jugador = pd.DataFrame([datos_jugador])
csv_filename = f"data/detalles_{jugador_buscado.replace(' ', '_')}.csv"
df_jugador.to_csv(csv_filename, index=False, encoding='utf-8')

print(f"✅ Datos de {jugador_buscado} guardados en '{csv_filename}'")

# Cerrar navegador
driver.quit()
print("🎉 Scraping finalizado.")
