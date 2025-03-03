from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import sys
import os
import requests

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

# URL de Sofascore
url_base = "https://www.sofascore.com/tournament/football/argentina/primera-nacional/703#id:71009,tab:details"
driver.get(url_base)

# Esperar que la página cargue completamente
wait = WebDriverWait(driver, 15)
time.sleep(5)  # Espera inicial

# 🔄 Buscar el jugador DESDE LA ÚLTIMA PÁGINA HACIA ATRÁS
pagina_actual = 41  # Última página
encontrado = False
url_jugador = None

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
                    for enlace in enlaces:
                        url_relativa = enlace.get_attribute("href")
                        if "/player/" in url_relativa:  # Verificar que sea la URL de un jugador
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

# Extraer información básica del jugador
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
    datos_jugador["Valor de Mercado"] = driver.find_element(By.CLASS_NAME, "imGAlA").text
except:
    datos_jugador["Valor de Mercado"] = "No disponible"

# Extraer el Heatmap
try:
    heatmap_section = driver.find_element(By.ID, "player-page-heatmap")
    
    # Definir la ruta para guardar la imagen
    heatmap_path = f"data/player/heatmap_{jugador_buscado.replace(' ', '_')}.png"
    
    # Tomar una captura de pantalla del heatmap
    heatmap_section.screenshot(heatmap_path)
    
    print(f"📸 Heatmap guardado en '{heatmap_path}'")
    datos_jugador["Heatmap"] = heatmap_path  # Guardamos la referencia en el CSV
except Exception as e:
    print(f"⚠ No se pudo capturar el heatmap: {e}")
    datos_jugador["Heatmap"] = "No disponible"

# 📸 **Descargar la imagen del jugador desde la URL de Sofascore**
try:
    # Extraer la URL de la imagen desde el HTML
    image_element = driver.find_element(By.XPATH, "//img[contains(@class,'Img')]")
    image_url = image_element.get_attribute("src")

    if image_url:
        # Definir la ruta para guardar la imagen
        player_image_path = f"data/player/{jugador_buscado.replace(' ', '_')}.png"
        
        # Descargar la imagen
        img_data = requests.get(image_url).content
        with open(player_image_path, 'wb') as handler:
            handler.write(img_data)
        
        print(f"🖼 Imagen del jugador guardada en '{player_image_path}'")
        datos_jugador["Imagen"] = player_image_path  # Guardamos la referencia en el CSV
    else:
        print("⚠ No se encontró la URL de la imagen del jugador.")
        datos_jugador["Imagen"] = "No disponible"

except Exception as e:
    print(f"⚠ Error al obtener la imagen del jugador: {e}")
    datos_jugador["Imagen"] = "No disponible"

# 📊 Scrapeo de Estadísticas por Categoría
categorias = ["Matches", "Attacking", "Passing", "Defending", "Other (per game)", "Cards"]
estadisticas = {}

for categoria in categorias:
    try:
        print(f"📂 Extrayendo estadísticas de {categoria}...")

        # Hacer clic en la categoría
        boton = wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(),'{categoria}')]")))
        driver.execute_script("arguments[0].click();", boton)
        time.sleep(3)  # Esperar carga de la sección

        # Extraer estadísticas de la tabla
        seccion = driver.find_element(By.XPATH, f"//span[contains(text(),'{categoria}')]/ancestor::button/following-sibling::div")
        filas = seccion.find_elements(By.CLASS_NAME, "Box")

        stats = {}
        for fila in filas:
            try:
                clave = fila.find_element(By.XPATH, ".//span[contains(@class,'Text')]").text.strip()
                valor = fila.find_elements(By.XPATH, ".//span[contains(@class,'Text')]")[-1].text.strip()
                stats[clave] = valor
            except:
                continue  # Si hay un error, pasar a la siguiente fila

        estadisticas[categoria] = stats
    except Exception as e:
        print(f"⚠ No se pudo obtener estadísticas de {categoria}: {e}")

# 📁 Guardar en CSV
df_basico = pd.DataFrame([datos_jugador])
df_basico.to_csv(f"data/player/player_details/detalles_{jugador_buscado.replace(' ', '_')}.csv", index=False, encoding='utf-8')

# Guardar estadísticas en CSV
for categoria, stats in estadisticas.items():
    df_stats = pd.DataFrame(stats.items(), columns=["Estadística", "Valor"])
    df_stats.to_csv(f"data/player/player_details/{jugador_buscado.replace(' ', '_')}_{categoria}.csv", index=False, encoding='utf-8')

print(f"✅ Datos de {jugador_buscado} guardados correctamente.")

# Cerrar navegador
driver.quit()
print("🎉 Scraping finalizado.")


# python -m src.scraping.scraper_player_details "Cristian Bernardi"
