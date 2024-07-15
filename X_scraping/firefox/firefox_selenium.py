import random
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from beautifulsoup_analisys import analisys_with_beautifulsoup
from utils import primary_keywords, secondary_keywords, read_json, connect_to_mongo, connect_to_mongo_collection

# Leggo file con credenziali
credentials = read_json("utils/credentials.json")

l = 0 # Parametro che indica quante parole chiave usare oltre al nome del gruppo di interesse. Può essere imostato a 0, 1 o 2.

# Connessione al DB per estrapolare la lista dei target sui quali far partire la ricerca
client = connect_to_mongo()
targets_collection = connect_to_mongo_collection(client, "target_groups")
documents = targets_collection.find()
target_list = [doc['name'] for doc in documents]


# Geckodriver
service = Service('driver/geckodriver')

# Inizializzo driver  Firefox
driver = webdriver.Firefox(service=service)
# driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

# Loggarsi manualmente su Twitter
driver.get('https://www.twitter.com/login')

# Imposto un'attesa esplicita di massimo 60 secondi
wait_login = WebDriverWait(driver, 60)

# Aspetto che un campo di ricerca con ID 'search-input' sia visibile
search_input_login = wait_login.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input')))

time.sleep(1)

# Cerco i campi nei quali far inserire automaticamente le credenziali
try:
    email_field = driver.find_element(By.XPATH, '/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input')
    email_field.send_keys(credentials["email"])
    email_field.send_keys(Keys.RETURN)
    time.sleep(2)
except NoSuchElementException:
    print("Campo email non trovato..")

# Controllo anche il campo username poiché dopo tanti accessi consecutivi X richiede anche lo username per sicurezza
try:
    username_field = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input')
    username_field.send_keys(credentials["username"])
    username_field.send_keys(Keys.RETURN)
    time.sleep(2)
except NoSuchElementException:
    print("Campo username non trovato..")

try:
    password_field = driver.find_element(By.XPATH, '/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input')
    password_field.send_keys(credentials["password"])
    password_field.send_keys(Keys.RETURN)
    time.sleep(2)
except NoSuchElementException:
    print("Campo password non trovato..")


for group in target_list:
    print(f"{group} in lavorazione..")

    keyword1 = random.choice(primary_keywords)
    keyword2 = random.choice(secondary_keywords)

    # Mando richiesta get con query nei parametri
    if l == 0:
        search_url = f"https://x.com/search?f=top&q={group}%20lang%3Aen%20-filter%3Alinks%20-filter%3Areplies&src=typed_query"
    elif l == 1:
        search_url = f"https://x.com/search?q={group}%20{keyword1}%20lang%3Aen%20-filter%3Alinks%20-filter%3Areplies&src=typed_query"
    elif l == 2:
        search_url = f"https://x.com/search?q={group}%20{keyword1}%20{keyword2}%20lang%3Aen%20-filter%3Alinks%20-filter%3Areplies&src=typed_query"
    else:
        search_url = f"https://x.com/search?q={group}&src=typed_query"

    driver.get(search_url)

    # Attendo caricamento pagina
    wait_tweets = WebDriverWait(driver, 120)

    # Aspettare che un elemento indicativo del completo caricamento della pagina sia visibile
    search_tweets = wait_tweets.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/section/div')))

    # Scorri la pagina verso il basso per caricare più tweet
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Attendi il caricamento della pagina
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Estraggo HTML pagina con BeautifulSoup e lo stampo
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    # Salvo la risposta in un file HTML
    with open(f'data_results/{group}.html', 'w') as f:
        f.write(soup.prettify())

    analisys_with_beautifulsoup(soup.prettify(), group)
driver.quit()
