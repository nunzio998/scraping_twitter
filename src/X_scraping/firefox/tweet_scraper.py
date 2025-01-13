"""
Questo script automatizza il processo di scraping di tweet da X (precedentemente noto come Twitter) per raccogliere informazioni
relativi a gruppi hacker, come indicato in un report sulla cybersecurity del 2024. L'obiettivo principale è eseguire una
ricerca su X per estrarre i tweet pertinenti a specifici gruppi hacker, raccogliendo vari dettagli come autore, contenuto, URL,
video, immagini, e il gruppo hacker di riferimento. Tutti i dati raccolti vengono quindi salvati nel database MongoDB per un
eventuale utilizzo futuro.

**Funzionamento del Processo**:\n
1. **Connessione al Database**: Lo script si connette a un database MongoDB per recuperare i gruppi target (gruppi hacker) definiti nella collection `target_groups`. Questi gruppi sono utilizzati come base per la ricerca dei tweet.

2. **Preparazione per l'Automazione del Browser**: Utilizzando Selenium e il driver Firefox in modalità "headless" (senza interfaccia grafica), viene configurato il browser per l'automazione della navigazione su X. Questo approccio consente di simulare l'interazione umana con il sito in modo che lo scraping possa essere effettuato automaticamente.

3. **Login su X**: Lo script esegue un login automatizzato a X utilizzando le credenziali memorizzate in un file JSON. La parte di login è manuale attraverso l'uso di un'apposita funzione, per garantire la sicurezza delle credenziali.

4. **Costruzione della Ricerca**: Per ogni gruppo target, viene costruito un URL di ricerca personalizzato. Questo URL filtra i tweet relativi al gruppo target, utilizzando le parole chiave scelte e limitando i risultati a quelli pubblicati tra la data dell'ultimo aggiornamento e quella odierna.

5. **Caricamento e Raccolta dei Tweet**:
   - Lo script naviga nella pagina di ricerca su X, dove i tweet vengono caricati dinamicamente.
   - Per garantire di raccogliere tutti i tweet disponibili, viene eseguita una scrollata continua della pagina, caricando tweet aggiuntivi ogni volta che la pagina si aggiorna.

6. **Estrazione e Analisi del Contenuto**:
   - Una volta caricati i tweet, l'HTML della pagina viene estratto utilizzando Selenium.
   - Il contenuto viene quindi analizzato tramite BeautifulSoup, che struttura e filtra i tweet in modo che possano essere facilmente utilizzati e salvati nel database.

7. **Salvataggio dei Dati nel Database**: Le informazioni estratte dai tweet (come autore, contenuto, URL, immagini, video e gruppo hacker di riferimento) vengono parsate e salvate nel database MongoDB per una successiva consultazione o analisi.

8. **Gestione degli Aggiornamenti**: Alla fine di ogni esecuzione, lo script aggiorna la data dell'ultimo aggiornamento nel database, in modo che nelle esecuzioni future lo script possa raccogliere solo i tweet nuovi, risparmiando tempo e risorse.

9. **Gestione degli Errori**: Se non vengono trovati risultati per un gruppo target o se si verificano problemi nel caricare una pagina (ad esempio, a causa di un errore di rete o di un timeout), lo script continua automaticamente con il gruppo successivo, senza interrompere l'intero processo di scraping.

10. **Chiusura delle Risorse**: Alla fine del processo, il driver Selenium viene chiuso correttamente, e la connessione al database MongoDB viene terminata, liberando risorse e chiudendo tutte le connessioni attive.

**Obiettivo**:\n
Il principale scopo di questo script è raccogliere informazioni utili dai tweet pubblici relativi ai gruppi hacker, al fine di monitorare le attività dei gruppi di interesse in un contesto di sicurezza informatica. Ogni esecuzione dello script consente di ottenere dati aggiornati e pertinenti, che possono essere analizzati per osservare eventuali tendenze o comportamenti sospetti.

**Autore**: Francesco Pinsone.
"""
import logging
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
    Funzione che automatizza la raccolta dei tweet da X (precedentemente noto come Twitter) per gruppi target predefiniti.
    Il processo comprende il login su X, la ricerca di tweet relativi a ciascun gruppo, e l'estrazione delle informazioni
    pertinenti da ciascun tweet. Le informazioni estratte vengono quindi salvate nel database MongoDB.

    **Funzionamento**:\n
    1. **Connessione al Database**: La funzione inizia con la connessione al database MongoDB, dove vengono recuperati i gruppi target dalla collection "target_groups". Ogni gruppo target corrisponde a una ricerca di tweet specifica su X.

    2. **Configurazione del Browser**: Utilizzando Selenium e il driver Firefox in modalità "headless" (senza interfaccia grafica), viene configurato il browser per interagire automaticamente con il sito X.

    3. **Login su X**: Dopo aver configurato il browser, la funzione esegue il login su X utilizzando le credenziali fornite tramite un file JSON.

    4. **Creazione della Ricerca**: Per ogni gruppo target:\n
       - Viene costruito un URL di ricerca personalizzato che include la data odierna e la data dell'ultimo aggiornamento per filtrare i tweet.\n
       - Viene eseguita una ricerca su X per ottenere i tweet relativi a quel gruppo, limitando i risultati a quelli pubblicati tra la data dell'ultimo aggiornamento e quella odierna.\n

    5. **Raccolta dei Tweet**: Una volta caricata la pagina con i risultati della ricerca:\n
       - Viene eseguita una scrollata della pagina per caricare i tweet aggiuntivi.\n
       - L'HTML della pagina viene estratto e analizzato con BeautifulSoup, che filtra e organizza i tweet trovati.\n

    6. **Estrazione e Salvataggio delle Informazioni**: I tweet estratti vengono parsati in una struttura utile, quindi vengono salvati nel database MongoDB.

    7. **Aggiornamento della Data di Riferimento**: Una volta completata l'operazione di scraping, la data dell'ultimo aggiornamento viene registrata nel database per essere utilizzata nelle future esecuzioni dello script.

    8. **Gestione degli Errori**: Se non vengono trovati risultati per un gruppo target o se si verificano errori durante il caricamento della pagina, lo script continua con il gruppo successivo senza interrompere l'esecuzione.

    Alla fine, il driver di Selenium viene chiuso e la connessione al database viene terminata.

    :return: Nessun valore ritornato. Le informazioni vengono salvate nel database.
    """
    # Configuro il logger
    logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                        format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log

    # Leggo file con credenziali
    credentials = read_json("utils/conf.json")

    # Connessione al DB
    client = connect_to_mongo()

    # Estrapolazione della lista di target su cui far partire la ricerca
    targets_collection = connect_to_mongo_collection(client, "target_groups")
    documents = targets_collection.find()
    target_list = [doc['name'] for doc in documents]

    # TODO valutare modifica alla modalità di ricerca tramite gruppi target

    # Configura opzioni del browser
    firefox_options = Options()
    # firefox_options.add_argument("--headless")

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

        logging.info(f"{group} in lavorazione..")

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
            logging.exception(f"Nessun risultato per {group}..")
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
