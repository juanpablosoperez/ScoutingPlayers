from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Diccionario con las posiciones y sus respectivos data-tabid
tabs = {
    "summary": "Resumen",
    "attack": "Ataque",
    "defence": "Defensa",
    "passing": "Pases",
    "goalkeeper": "Porteros"
}

# Configurar el WebDriver
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Ejecutar sin abrir ventana (opcional)
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=options)

# URL de la página principal de la B Nacional
driver.get("https://www.sofascore.com/tournament/football/argentina/primera-nacional/703#id:71009,tab:details")
time.sleep(5)  # Esperamos que cargue la página

for tab_id, tab_name in tabs.items():
    print(f"📊 Scrapeando datos de {tab_name}...")

    try:
        # Click en la pestaña correspondiente
        tab_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[@data-tabid='{tab_id}']"))
        )
        driver.execute_script("arguments[0].click();", tab_button)
        time.sleep(3)  # Esperamos que cargue la tabla

        all_players = []
        page = 1

        while True:
            print(f"📄 Scrapeando página {page} de {tab_name}...")

            try:
                # Esperar a que la tabla esté presente
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )

                table = driver.find_element(By.TAG_NAME, "table")
                rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Omitimos el header
                
                for row in rows:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) > 1:
                        player_data = [col.text for col in cols]
                        all_players.append(player_data)

                # Intentar hacer clic en el botón de siguiente página si está habilitado
                try:
                    next_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'Button') and not(@disabled)]/svg/path[@d='M18 12.01 9.942 20 8.51 18.58l6.636-6.57L8.5 5.41 9.922 4z']/ancestor::button"))
                    )
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(3)  # Esperamos a que la nueva página cargue
                    page += 1
                except:
                    print(f"✅ No hay más páginas en {tab_name}.")
                    break

            except Exception as e:
                print(f"⚠️ Error en la página {page} de {tab_name}: {e}")
                break

        # Guardar datos en CSV
        df = pd.DataFrame(all_players)
        df.to_csv(f"data/jugadores_{tab_id}.csv", index=False, encoding='utf-8')
        print(f"✅ Datos de {tab_name} guardados en 'data/jugadores_{tab_id}.csv'")

    except Exception as e:
        print(f"❌ Error al scrapeando {tab_name}: {e}")

driver.quit()
print("🎉 Scraping finalizado para todas las posiciones.")
