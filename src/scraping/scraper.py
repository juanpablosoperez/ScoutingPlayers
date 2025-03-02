from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

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

# Lista para almacenar nombres de jugadores
jugadores_lista = []

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
            if len(columnas) >= 3:  # Verificar que tenga al menos la columna del jugador
                nombre = columnas[2].text.strip()
                if nombre:
                    jugadores_lista.append(nombre)

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

# 📋 Mostrar la lista de jugadores disponibles
print("\n📋 Lista de jugadores disponibles:")
for i, nombre in enumerate(jugadores_lista, start=1):
    print(f"{i}. {nombre}")

# 🎯 Pedir al usuario que seleccione un jugador
while True:
    try:
        seleccion = int(input("\nIngrese el número del jugador a analizar: "))
        if 1 <= seleccion <= len(jugadores_lista):
            jugador_buscado = jugadores_lista[seleccion - 1]
            print(f"📊 Buscando a {jugador_buscado} desde la última página...")
            break
        else:
            print("❌ Número fuera de rango. Intente de nuevo.")
    except ValueError:
        print("❌ Entrada inválida. Ingrese un número válido.")

# 🔄 Buscar el jugador DESDE LA ÚLTIMA PÁGINA HACIA ATRÁS
pagina_actual = paginas_totales
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
                    print(f"✅ Jugador {jugador_buscado} encontrado. Abriendo su perfil...")

                    # Hacer clic en el enlace del jugador
                    enlace_jugador = fila.find_element(By.TAG_NAME, "a")
                    driver.execute_script("arguments[0].click();", enlace_jugador)
                    time.sleep(5)  # Esperar carga del perfil
                    encontrado = True
                    break

        if encontrado:
            break  # Salir del bucle si el jugador fue encontrado

        # Ir a la página anterior (REVISADO)
        try:
            boton_anterior = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@class="Button llwjsV" and not(@disabled)]')))
            driver.execute_script("arguments[0].click();", boton_anterior)
            time.sleep(4)
        except Exception:
            print("⚠ No se encontró el botón de página anterior. Intentando nuevamente...")
            break

    except Exception as e:
        print(f"❌ Error buscando al jugador: {e}")
        break

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
