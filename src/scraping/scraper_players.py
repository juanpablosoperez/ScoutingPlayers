import os
import csv
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configurar Selenium
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

# Lista para almacenar nombres de jugadores
jugadores_lista = []
paginas_totales = 41  # Número total de páginas

for pagina in range(1, paginas_totales + 1):
    print(f"📄 Scrapeando página {pagina} de {paginas_totales}...")

    try:
        tabla = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "kLmlmP")))
        filas = tabla.find_elements(By.TAG_NAME, "tr")

        for fila in filas:
            columnas = fila.find_elements(By.TAG_NAME, "td")
            if len(columnas) >= 3:
                nombre = columnas[2].text.strip()
                if nombre:
                    jugadores_lista.append(nombre)

        try:
            boton_siguiente = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@class="Button llwjsV" and @style="justify-content: flex-end;"]')))
            driver.execute_script("arguments[0].click();", boton_siguiente)
            time.sleep(4)
        except Exception:
            print("⚠ No se encontró el botón de siguiente página. Fin del scraping.")
            break

    except Exception as e:
        print(f"❌ Error en la página {pagina}: {e}")
        break

driver.quit()

# Guardar los nombres en un archivo CSV
csv_filename = "data/jugadores_lista.csv"
os.makedirs("data", exist_ok=True)  # Crear carpeta si no existe

with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Nombre"])  # Cabecera
    for jugador in jugadores_lista:
        writer.writerow([jugador])

print(f"\n✅ {len(jugadores_lista)} jugadores guardados en '{csv_filename}'.")

# Mostrar la lista de jugadores disponibles
print("\n📋 Lista de jugadores disponibles:")
for i, nombre in enumerate(jugadores_lista, start=1):
    print(f"{i}. {nombre}")

# Pedir al usuario que seleccione un jugador
while True:
    try:
        seleccion = int(input("\nIngrese el número del jugador a analizar: "))
        if 1 <= seleccion <= len(jugadores_lista):
            jugador_buscado = jugadores_lista[seleccion - 1]
            print(f"📊 Analizando a {jugador_buscado}...")
            break
        else:
            print("❌ Número fuera de rango. Intente de nuevo.")
    except ValueError:
        print("❌ Entrada inválida. Ingrese un número válido.")

# Ejecutar el segundo script pasando el nombre del jugador como argumento
subprocess.run(["python", "src/scraping/scraper_player_details.py", jugador_buscado])
