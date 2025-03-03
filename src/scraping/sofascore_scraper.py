from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Configurar Selenium con opciones avanzadas
chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument("--headless")  # Ejecutar en segundo plano
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

# Lista para almacenar datos
jugadores_data = []

# Número total de páginas (41)
paginas_totales = 41

for pagina in range(1, paginas_totales + 1):
    print(f"📄 Scrapeando página {pagina} de {paginas_totales}...")

    try:
        # Esperar a que la tabla cargue
        tabla = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "kLmlmP")))

        # Extraer filas de la tabla
        filas = tabla.find_elements(By.TAG_NAME, "tr")

        for fila in filas:
            columnas = fila.find_elements(By.TAG_NAME, "td")
            if len(columnas) >= 7:
                rank = columnas[0].text.strip()
                equipo = columnas[1].get_attribute("title")  # Extraer nombre del equipo
                nombre = columnas[2].text.strip()
                goles = columnas[3].text.strip()
                dribbles = columnas[4].text.strip()
                tackles = columnas[5].text.strip()
                asistencias = columnas[6].text.strip()
                precision_pases = columnas[7].text.strip()
                rating = columnas[8].text.strip()

                jugadores_data.append([
                    rank, equipo, nombre, goles, dribbles, tackles, asistencias, precision_pases, rating
                ])

        # Intentar hacer clic en el botón de siguiente página
        try:
            boton_siguiente = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@class="Button llwjsV" and @style="justify-content: flex-end;"]')))
            driver.execute_script("arguments[0].click();", boton_siguiente)
            time.sleep(4)  # Espera tras cambiar de página
        except Exception:
            print("⚠ No se encontró el botón de siguiente página. Fin del scraping.")
            break

    except Exception as e:
        print(f"❌ Error en la página {pagina}: {e}")
        break

# Cerrar el navegador
driver.quit()

# Guardar los datos en un archivo CSV
df = pd.DataFrame(jugadores_data, columns=["Rank", "Equipo", "Nombre", "Goles", "Dribbles Exitosos", "Tackles", "Asistencias", "Precisión Pases %", "Rating"])
df.to_csv("data/player/players/jugadores_primera_nacional.csv", index=False, encoding="utf-8")
print(f"✅ Scraping completado. {len(jugadores_data)} jugadores guardados en 'data/player/players/jugadores_primera_nacional.csv'")
