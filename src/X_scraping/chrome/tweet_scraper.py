"""
Lo script ha il compito di effettuare un'attività di scraping su X andando a fare ricerca dei tweet per parole chiave.
Sulla base di un report sulla cybersecurity del 2024 sono stati scelti i nomi di una serie di gruppi hacker come target list
iniziale sulla quale far lavorare lo script. Ad ogni esecuzione lo script effettua una ricerca su X ed estrae i tweet che ne risultano.
Per ogni tweet vengono salvate diverse informazioni: autore, contenuto, url, gruppo hacker di riferimento, immagini e video contenuti.\n

Autore: Francesco Pinsone.
"""
import random
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.X_scraping.chrome.utils.utils import primary_keywords, secondary_keywords, read_json, connect_to_mongo, \
    connect_to_mongo_collection, disconnect_to_mongo, read_parse_save, x_login
from src.X_scraping.chrome.beautifulsoup_analisys import analisys_with_beautifulsoup


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

    l = -1  # Parametro che indica quante parole chiave usare oltre al nome del gruppo di interesse. Può essere imostato a 0, 1 o 2.

    # Connessione al DB per estrapolare la lista dei target sui quali far partire la ricerca
    client = connect_to_mongo()
    targets_collection = connect_to_mongo_collection(client, "target_groups")
    documents = targets_collection.find()
    target_list = [doc['name'] for doc in documents]
    disconnect_to_mongo(client)

    # TODO valutare modifica all'url di ricerca dei tweet e alla modalità di ricerca tramite gruppi target

    chrome_options = Options()

    # Gestore del driver per semplificare la gestione del driver Chrome
    # N.B: Scaricare chromedriver e cambiare executable_path con il path del driver scaricato
    service = Service(executable_path=credentials['driver_path'])

    # Creare un'istanza del browser Chrome con le opzioni
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Loggarsi manualmente su Twitter
    driver.get('https://www.twitter.com/login')

    # Imposto un'attesa esplicita di massimo 60 secondi
    wait_login = WebDriverWait(driver, 60)

    # Aspetto che un campo di ricerca con ID 'search-input' sia visibile
    search_input_login = wait_login.until(EC.visibility_of_element_located((By.XPATH,
                                                                            '/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input')))

    # Effettuo il login ad X
    x_login(credentials, driver)

    for group in target_list:
        client = connect_to_mongo()
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

        try:
            driver.get(search_url)

            # Attendo caricamento pagina
            wait_tweets = WebDriverWait(driver, 120)

            # Aspettare che un elemento indicativo del completo caricamento della pagina sia visibile
            search_tweets = wait_tweets.until(EC.visibility_of_element_located(
                (By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/section/div')))
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

        # Salvo la risposta in un file HTML
        with open(f'data_results/{group}.html', 'w') as f:
            f.write(soup.prettify())

        res = analisys_with_beautifulsoup(soup.prettify())

        # Divido le info in post e le salvo nel database
        read_parse_save(res, group, client)

        disconnect_to_mongo(client)

        # TODO: ristrutturare codice a partire dalla funzione analisys_with_beautifulsoup

    driver.quit()


if __name__ == "__main__":
    scrape_tweets()
