from selenium import webdriver
from selenium.webdriver.firefox.service import Service
import time
from bs4 import BeautifulSoup
from utils import interest_groups

# Geckodriver
service = Service('driver/geckodriver')

# Inizializzo driver  Firefox
driver = webdriver.Firefox(service=service)
# driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

# Loggarsi manualmente su Twitter
driver.get('https://www.twitter.com/login')
input("Premi Enter dopo aver effettuato il login...")

for group in interest_groups:
    # Mando richiesta get con query nei parametri
    search_url = f"https://x.com/search?f=top&q={group}%20lang%3Aen%20-filter%3Alinks%20-filter%3Areplies&src=typed_query"
    driver.get(search_url)

    # Attendo caricamento pagina
    time.sleep(5)

    # Estraggo HTML pagina con BeautifulSoup e lo stampo
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    # Salvo la risposta in un file HTML
    with open(f'data_results/{group}.html', 'w') as f:
        f.write(soup.prettify())

driver.quit()
