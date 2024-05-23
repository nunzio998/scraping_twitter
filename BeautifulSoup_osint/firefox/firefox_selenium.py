from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import json
from bs4 import BeautifulSoup
from selenium.webdriver import FirefoxService
from webdriver_manager.firefox import GeckoDriverManager


fp = webdriver.FirefoxProfile()


fp.set_preference("browser.download.folderList",2)

fp.set_preference("javascript.enabled", True)

# Geckodriver
service = Service('driver/geckodriver')

# Inizializzo driver  Firefox
options = webdriver.FirefoxOptions()

# Opzioni driver (su browser con about:support)
options.add_argument('--user-data-dir=/Users/francesco/Library/Application Support/Firefox/Profiles/i5qodkh1.default-release-1716024453688')# Questo utilizza il tuo profilo Firefox
options.add_argument("javascript.enabled")

driver = webdriver.Firefox(service=service, options=options)
#driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

# Loggarsi manualmente su Twitter
driver.get('https://www.twitter.com/login')
input("Premi Enter dopo aver effettuato il login...")

# Mando richiesta get con query nei parametri
#search_url = 'https://x.com/search?q=killnet&src=typed_query'
search_url = "https://x.com/search?f=top&q=Killnet%20lang%3Aen%20-filter%3Alinks%20-filter%3Areplies&src=typed_query"
driver.get(search_url)

# Attendo caricamento pagina
time.sleep(5)

# Estraggo HTML pagina con BeautifulSoup e lo stampo
html_content = driver.page_source
soup = BeautifulSoup(html_content, 'html.parser')

# Salvo la risposta in un file HTML
with open('data_results/response.html', 'w') as f:
    f.write(soup.prettify())

driver.quit()
