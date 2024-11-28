"""
Lo script ha il compito di effettuare un'attività di scraping su X andando a fare ricerca dei tweet per parole chiave.
Sulla base di un report sulla cybersecurity del 2024 sono stati scelti i nomi di una serie di gruppi hacker come target list
iniziale sulla quale far lavorare lo script. Ad ogni esecuzione lo script effettua una ricerca su X ed estrae i tweet che ne risultano.
Per ogni tweet vengono salvate diverse informazioni: autore, contenuto, url, gruppo hacker di riferimento, immagini e video contenuti.\n

Autore: Francesco Pinsone.
"""
import random
import time
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from src.X_scraping.firefox.utils.utils import primary_keywords, secondary_keywords, read_json, connect_to_mongo, \
    connect_to_mongo_collection, disconnect_to_mongo, parse_and_save, x_login
from src.X_scraping.firefox.beautifulsoup_analisys import analisys_with_beautifulsoup


def scrape_tweets():
    """
    Funzione che racchiude l'intero funzionamento dello script.\n
    Dopo aver effettuato la connessione a MondoDB e inizializzato il driver selenium per l'automazione del browser effettua il
    login ad X. Subito dopo per ogni target effettua la ricerca e filtra il contenuto della pagina html che ottiene al fine di
    ottenere una lista di elementi relativi a tutti i tweet trovati. Questo insieme di informazioni viene dapprima diviso, per
    differenziare i vari elementi, e poi parsato per ottenere i tweet nel giusto formato da poter poi salvare nel db.\n
    :return None:
    """
    # Leggo file con credenziali
    credentials = read_json("utils/credentials.json")

    # Connessione al DB
    client = connect_to_mongo()

    # Estrapolazione della lista di target su cui far partire la ricerca
    targets_collection = connect_to_mongo_collection(client, "target_groups")
    documents = targets_collection.find()
    target_list = [doc['name'] for doc in documents]

    # TODO valutare modifica alla modalità di ricerca tramite gruppi target

    # Configura opzioni del browser
    firefox_options = Options()
    firefox_options.add_argument("--headless")

    # Geckodriver
    service = Service('driver/geckodriver')

    # Inizializzo driver  Firefox
    driver = webdriver.Firefox(service=service, options=firefox_options)
    # driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

    # Loggarsi manualmente su Twitter
    driver.get('https://www.twitter.com/login')

    # Imposto un'attesa esplicita di massimo 60 secondi
    wait_login = WebDriverWait(driver, 60)

    # Aspetto che un campo di ricerca con ID 'search-input' sia visibile
    search_input_login = wait_login.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input')))

    time.sleep(1)

    # Effettuo il login a X
    x_login(credentials, driver)

    # Imposto la data odierna e ottengo l'ultima data di aggiornamento
    today = datetime.today().strftime('%Y-%m-%d')

    coll = connect_to_mongo_collection(client, "last_update")

    last_update = coll.find_one({"id": "01"}).get("last_update")

    for group in target_list:

        print(f"{group} in lavorazione..")

        # keyword1 = random.choice(primary_keywords)
        # keyword2 = random.choice(secondary_keywords)
        #
        # search_url = f"https://x.com/search?q={group}%20{keyword1}%20{keyword2}%20lang%3Aen%20-filter%3Alinks%20-filter%3Areplies&src=typed_query"

        search_url = f"https://x.com/search?q={group}%20until%3A{today}%20since%3A{last_update}%20-filter%3Areplies&src=typed_query"

        try:
            driver.get(search_url)

            # Attendo caricamento pagina
            wait_tweets = WebDriverWait(driver, 60)

            # Aspettare che un elemento indicativo del completo caricamento della pagina sia visibile
            search_tweets = wait_tweets.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/section/div')))
        except TimeoutException:
            print(f"Nessun risultato per {group}..")
            continue

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

        res = analisys_with_beautifulsoup(soup.prettify())

        # Divido le info in post e le salvo nel database
        parse_and_save(res, group, client)

    # Salvo la nuova data di ultimo aggiornamento, mi disconnetto da MongoDB e chiudo il driver.
    coll = connect_to_mongo_collection(client, "last_update")
    coll.update_one({"id": "01"}, {"$set": {"last_update": today}})
    disconnect_to_mongo(client)
    driver.quit()


if __name__ == "__main__":
    scrape_tweets()
