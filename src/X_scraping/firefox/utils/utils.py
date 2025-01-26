"""
Questo script fornisce una serie di funzioni utili per interagire con il sito web di X, eseguire scraping dei messaggi in una chat e interagire con un database MongoDB. Le funzionalità principali incluse in questo script sono:

1. **Gestione MongoDB**:\n
   - Connessione a un database MongoDB tramite una stringa di connessione.\n
   - Connessione a specifiche collezioni MongoDB, con la possibilità di crearle se non esistono.\n
   - Salvataggio dei dati nel database MongoDB.\n

2. **Analisi dei dati con BeautifulSoup**:\n
   - Estrazione e parsing dei dati da una pagina web tramite il modulo BeautifulSoup.\n

3. **Interazioni con X tramite Selenium**:\n
   - Automazione del login a X usando Selenium.\n
   - Navigazione tra le pagine di X per raccogliere messaggi da una chat.\n
   - Scroll della pagina per caricare più messaggi tramite l'interazione con la pagina HTML.\n

4. **Check dei dati**:\n
   - Check dei dati estratti.\n

5. **Logging**:\n
   - Logging delle operazioni eseguite per monitorare l'avanzamento e il successo o il fallimento delle azioni (ad esempio, la connessione al database, l'esecuzione dello scraping, il login a X, ecc.).\n

**Prerequisiti**:\n
- Una connessione attiva a un database MongoDB.\n
- Un ambiente con Selenium e BeautifulSoup per l'automazione del browser e l'analisi del contenuto delle pagine.\n

**Autore**: Francesco Pinsone.
"""
import json
import re
import time
from datetime import datetime
import pymongo
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

# Configuro il logger
logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                    format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log


interest_groups = ["Killnet", "NoName057(16)", "Lazarus", "DarkHalo", "MustangPanda", "BlackEnergy", "BadMagic",
                   "DarkSide", "LockBit", "DopplePaymer", "RagnarLocker",
                   "REvil", "DragonFly"]

primary_keywords = ["hacker", "cyberwar", "cyber", "energy"]

secondary_keywords = ["italy", "europe", "group", "attack", "threat"]


def read_json(path) -> dict:
    """
    Funzione per leggere il contenuto di un file JSON e restituirlo come dizionario.

    **Funzionamento**:\n
    1. **Apertura del file**: Apre il file JSON specificato dal percorso `path` in modalità lettura.\n
    2. **Caricamento del contenuto**: Utilizza la funzione `json.load` per caricare il contenuto del file JSON e convertirlo in un oggetto Python (dizionario).\n
    3. **Restituzione dei dati**: Una volta letto il file, la funzione restituisce il dizionario contenente i dati del file JSON.\n

    :param path: str, il percorso del file JSON da leggere.\n
    :return: dict, i dati contenuti nel file JSON, rappresentati come un dizionario Python.
    """
    with open(path, 'r') as file:
        return json.load(file)


config_data = read_json('/Users/francesco/Documents/Campus Biomedico/2 anno/II Semestre/Tesi/python_workspace/src/X_scraping/firefox/utils/mongo_utils.json')


def x_login(credentials_access, driver_access) -> None:
    """
    La funzione `x_login` automatizza la procedura di accesso a X (Twitter) utilizzando il driver Selenium per il controllo del browser.
    Prende in input un dizionario contenente le credenziali di accesso (email, username e password) e il driver del browser.
    La funzione interagisce con i campi del modulo di login per inserire i dati necessari e simulare la pressione del tasto Invio.

    **Funzionalità principali**:\n
    1. **Inserimento dell'email:** La funzione cerca il campo per l'inserimento dell'email tramite il suo percorso XPath. Se il campo è presente, inserisce l'email fornita nelle credenziali e invia il modulo.\n
    2. **Gestione dello username (se richiesto):** In caso di richieste aggiuntive di sicurezza, come l'inserimento dello username, la funzione identifica il campo corrispondente e procede con l'inserimento e l'invio.\n
    3. **Inserimento della password:** La funzione individua il campo della password, inserisce il valore fornito nelle credenziali e completa il login simulando la pressione del tasto Invio.\n
    4. **Gestione degli errori:** Se uno dei campi non viene trovato (ad esempio, se l'interfaccia cambia), la funzione gestisce l'eccezione e stampa un messaggio di errore.\n

    **Comportamento della funzione**:\n
    1. Controlla e riempie il campo dell'email.\n
    2. Se richiesto, riempie il campo dello username.\n
    3. Inserisce la password e completa l'accesso.\n
    4. Effettua un breve ritardo dopo ogni interazione per garantire il caricamento delle pagine.

    **Utilità:**
    La funzione è utile per automatizzare l'accesso a X in applicazioni di scraping o altre automazioni, gestendo richieste di sicurezza aggiuntive come l'inserimento dello username.

    :param **credentials_access**: dict contenente le credenziali di accesso
    :param **driver_access**: oggetto Selenium WebDriver utilizzato per controllare il browser e interagire con l'interfaccia.
    :return: Nessun valore restituito.
    """

    try:
        email_field = driver_access.find_element(By.XPATH, '/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input')
        email_field.send_keys(credentials_access["email"])
        email_field.send_keys(Keys.RETURN)

        time.sleep(2)
    except NoSuchElementException:
        logging.info("Campo email non trovato..")

    # Controllo anche il campo username poiché dopo tanti accessi consecutivi X richiede anche lo username per sicurezza
    try:
        #username_field = driver_access.find_element(By.XPATH, '/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input')
        username_field = driver_access.find_element(By.XPATH, '/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input')
        username_field.send_keys(credentials_access["username"])
        username_field.send_keys(Keys.RETURN)

        time.sleep(2)
    except NoSuchElementException:
        logging.info("Campo username non trovato..")

    try:
        password_field = driver_access.find_element(By.XPATH, '/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input')
        password_field.send_keys(credentials_access["password"])
        password_field.send_keys(Keys.RETURN)

        time.sleep(2)
    except NoSuchElementException:
        logging.info("Campo password non trovato..")


# Funzioni MongoDB:
def connect_to_mongo() -> pymongo.MongoClient:
    """
    Funzione che consente di stabilire una connessione con un database MongoDB utilizzando una stringa di connessione.

    **Passaggi principali**:\n
    1. **Connessione al Database**: Utilizza la stringa di connessione predefinita, configurata nel file di configurazione, per stabilire la connessione con il server MongoDB.\n
    2. **Verifica della Connessione**: Esegue un comando `ping` sul database per verificare se la connessione è attiva. Se la connessione ha successo, viene registrato un log con la versione del server MongoDB.\n
    3. **Gestione degli Errori**: Se si verifica un errore durante il tentativo di connessione, l'errore viene registrato nel log.\n

    **Nota**: Il client MongoDB viene creato utilizzando la libreria `pymongo`, e la connessione viene stabilita utilizzando la stringa di connessione definita nel file di configurazione.\n

    :return: client, oggetto che rappresenta la connessione attiva al database MongoDB.
    """
    connection_string = config_data['connection_string']
    client = pymongo.MongoClient(connection_string)
    # Provo a connettermi al database
    try:
        client.admin.command('ping')
        logging.info(f"Connesso al database: {client.server_info()['version']}")
    except Exception as e:
        logging.exception(e)

    return client


def disconnect_to_mongo(client) -> None:
    """
    Funzione che consente di disconnettersi dal database MongoDB, chiudendo la connessione attiva.

    **Passaggi principali**:\n
    1. **Log della Disconnessione**: La funzione registra un log che indica la disconnessione dal database, includendo la versione del server MongoDB al quale era connesso.\n
    2. **Chiusura della Connessione**: Una volta eseguito il log, la connessione al database viene chiusa, liberando le risorse.\n

    **Nota**: La funzione utilizza il metodo `server_info()` per recuperare informazioni sul server, come la versione, che verranno incluse nel log.\n

    :param client: Oggetto di connessione al database MongoDB. Deve essere un client MongoDB valido, creato con una libreria come `pymongo`.\n
    :return: Nessun valore restituito. La funzione esegue solo l'azione di disconnessione dal database.
    """
    logging.info(f"Disconnesso dal database: {client.server_info()['version']}")
    client.close()


def get_db(client) -> pymongo.database.Database:
    """
    Funzione che restituisce un riferimento al database MongoDB specificato.

    La funzione utilizza un oggetto client di MongoDB per connettersi al database configurato nel file `conf.json`.
    È utile per ottenere un'istanza del database e interagire con le sue collezioni.

    :param client: oggetto che rappresenta la connessione a MongoDB.\n
    :return: oggetto che rappresenta la connessione al database specificato in 'conf.json'.
    """
    return client.get_database(config_data['database'])


def connect_to_mongo_collection(client, collection_name) -> pymongo.collection.Collection:
    """
    Funzione che consente di connettersi a una collezione specifica di MongoDB. Se la collezione non esiste, la funzione la crea automaticamente.

    **Passaggi principali**:\n
    1. **Connessione al Database**: La funzione si connette al database MongoDB utilizzando il client e il nome del database fornito nelle impostazioni.\n
    2. **Verifica e Creazione Collezione**: La funzione verifica se la collezione specificata esiste già nel database. Se non esiste, la funzione la crea.\n
    3. **Restituzione della Collezione**: Una volta verificata o creata la collezione, la funzione restituisce un oggetto che rappresenta la collezione, pronto per operazioni successive.\n

    **Nota**: La funzione assume che la configurazione del database (incluso il nome del database) sia disponibile attraverso un oggetto di configurazione (ad esempio `config_data`).\n

    :param client: Oggetto di connessione al database MongoDB. Deve essere un client MongoDB valido, creato con una libreria come `pymongo`.\n
    :param collection_name: Stringa che rappresenta il nome della collezione a cui ci si vuole connettere o che si vuole creare.\n
    :return: Oggetto che rappresenta la collezione MongoDB. La collezione sarà pronta per l'uso (lettura/scrittura).
    """
    db = client.get_database(config_data['database'])

    # Verifica se la collezione esiste già
    if collection_name not in db.list_collection_names():
        # Se la collezione non esiste, creala
        db.create_collection(collection_name)
        logging.info(f"Creata la collezione: {collection_name}")
    else:
        logging.info(f"La collezione esiste già: {collection_name}")

    return db.get_collection(collection_name)


def save_to_mongo(data, collection) -> None:
    """
    Funzione che salva i dati in una collezione di MongoDB. La funzione inserisce un singolo documento (dati) nella collezione specificata.

    **Passaggi principali**:\n
    1. **Salvataggio dei dati**: I dati vengono passati come un dizionario (`data`) e vengono inseriti nella collezione MongoDB fornita tramite il metodo `insert_one()`.\n
    2. **Logging**: Viene registrato un messaggio di log che conferma che i dati sono stati salvati nel database.\n

    **Nota**: Questa funzione salva i dati in un'unica operazione e non esegue controlli avanzati (ad esempio, verifica di duplicati o gestione di errori).\n

    :param data: dict, i dati da salvare nel database. Si suppone che siano nel formato appropriato per MongoDB (ad esempio, un dizionario Python).\n
    :param collection: Oggetto che rappresenta la collezione di MongoDB in cui i dati devono essere salvati.\n
    :return: Nessun valore restituito. La funzione esegue solo l'inserimento dei dati.
    """
    collection.insert_one(data)
    logging.info(f"Salvato nel database: {data['url']}")


def save_user_info_to_mongo(data, collection) -> None:
    """
    Funzione per salvare informazioni utente nel database MongoDB.

    Questa funzione consente di salvare un documento contenente i dati relativi a un utente in una specifica collezione del database MongoDB.
    È progettata per essere utilizzata nello script `user_info_scraper.py`, che richiede un approccio diverso rispetto alla funzione generica `save_to_mongo`.
    In particolare, dopo il salvataggio, l'attenzione è rivolta alla visualizzazione del tag dello username dell'utente, piuttosto che all'URL di un post salvato,
    rendendo questa funzione specifica per le esigenze dello script.

    :param data: dict, dizionario contenente i dati relativi all'utente da salvare.\n
    :param collection: oggetto che rappresenta la collezione MongoDB in cui salvare il documento.\n
    :return: Nessun valore restituito.
    """
    collection.insert_one(data)
    logging.info(f"Salvato nel database: {data['tag_username']}")


# config_data = read_json('mongo_utils.json')

def parse_tweet(tweet) -> dict or None:
    """
    Funzione per il parsing di un tweet in formato JSON.

    Questa funzione riceve in input una lista contenente le informazioni grezze di un tweet e restituisce un oggetto JSON ben strutturato,
    organizzando i dati in campi chiave per facilitarne l'analisi o l'archiviazione. È progettata per filtrare contenuti incompleti e
    estrarre solo le informazioni rilevanti, riformattandole per un utilizzo più pratico.

    **Struttura dell'oggetto restituito**:\n
    - `'username'`: Nome utente dell'autore del tweet.\n
    - `'tag_username'`: Tag dello username dell'autore del tweet (es. @username).\n
    - `'date'`: Data di pubblicazione del tweet.\n
    - `'scrape_date'`: Data in cui il tweet è stato estratto e analizzato.\n
    - `'content'`: Testo contenuto nel tweet.\n
    - `'reshared'`: Contenuto del post originale in caso di ricondivisione (retweet).\n
    - `'images'`: Lista di immagini incluse nel tweet.\n
    - `'videos'`: Lista di video inclusi nel tweet.\n
    - `'comments'`: Numero di commenti ricevuti.\n
    - `'reposts'`: Numero di repost o retweet.\n
    - `'likes'`: Numero di like ricevuti.\n
    - `'views'`: Numero di visualizzazioni totali.\n
    - `'url'`: URL diretto al tweet.\n

    **Gestione di eventuali discrepanze**:\n
    - Se i dati del tweet non contengono tutte le informazioni necessarie (ad esempio mancano valori numerici per i commenti, like, ecc.), i campi corrispondenti vengono riempiti con `None`.\n
    - I post con meno di 9 elementi vengono scartati automaticamente.\n

    :param tweet: list, lista contenente i dati del tweet in ordine predefinito.\n
    :return: dict, oggetto JSON contenente i dati strutturati del tweet, oppure `None` se i dati in ingresso sono incompleti.\n
    """
    if len(tweet) < 9:
        return None  # Skip invalid posts

    username = tweet[0]

    username_tag = tweet[1]

    data_pubblicazione = tweet[2]

    if tweet[3]:
        contenuto = ' '.join(tweet[3].split())
    else:
        contenuto = None

    ricondivisione = tweet[4]

    images = tweet[5]

    videos = tweet[6]

    numeri = re.findall(r'\d+\.?\d*', tweet[7])

    if len(numeri) == 4:
        commenti = numeri[0]
        repost = numeri[1]
        like = numeri[2]
        visualizzazioni = numeri[3]
    elif len(numeri) == 3:
        commenti = None
        repost = numeri[0]
        like = numeri[1]
        visualizzazioni = numeri[2]
    elif len(numeri) == 2:
        commenti = None
        repost = None
        like = numeri[0]
        visualizzazioni = numeri[1]
    elif len(numeri) == 1:
        commenti = None
        repost = None
        like = None
        visualizzazioni = numeri[0]
    else:
        commenti = None
        repost = None
        like = None
        visualizzazioni = None

    url = tweet[8]

    # Ritorno il post in formato json
    return {
        'username': username,
        'tag_username': username_tag,
        'date': data_pubblicazione,
        'scrape_date': datetime.today().strftime('%Y-%m-%d'),
        'content': contenuto,
        'reshared': ricondivisione,
        'images': images,
        'videos': videos,
        'comments': commenti,
        'reposts': repost,
        'likes': like,
        'views': visualizzazioni,
        'url': url
    }


def parse_and_save(tweets_to_save, collection) -> None:
    """
    Funzione per il parsing e il salvataggio di tweet nel database MongoDB.

    Questa funzione è utilizzata nello script `tweet_scraper.py` per elaborare e archiviare i tweet estratti da un file HTML.
    Riceve in ingresso una lista di righe HTML che rappresentano i vari tweet da processare. La funzione esegue le seguenti operazioni:\n

    1. **Raggruppamento e organizzazione dei tweet**: Utilizza la funzione `read_posts()` per trasformare la lista di righe HTML in una lista di tweet ben definiti.\n
    2. **Parsing dei tweet**: Ogni tweet viene processato con la funzione `parse_tweet()` per estrarre e organizzare le informazioni rilevanti.\n
    3. **Salvataggio nel database**: I tweet parsati vengono salvati nella collezione MongoDB corrispondente al nome del gruppo target.\n

    La funzione garantisce che solo i tweet validi vengano salvati nel database, ignorando quelli che risultano incompleti o malformati.

    :param **tweets_to_save** (list): Lista di righe HTML estratte, dove ogni riga rappresenta una parte di un tweet.\n
    :param **collection** (object): Oggetto che rappresenta la connessione alla collection MongoDB.\n
    :return: Nessun valore restituito:
    """

    # Parso ogni post e lo aggiungo al database
    for tweet in tweets_to_save:
        parsed_tweet = parse_tweet(tweet)
        # Salvo il post parsato nel database, se non è None
        if parsed_tweet and not is_url_in_db(parsed_tweet['url'], collection):
            save_to_mongo(parsed_tweet, collection)
        else:
            logging.info(f"Tweet non valido o già presente nel database: {parsed_tweet['url']}")


def check_user(driver, user) -> bool:
    """
    Funzione che verifica l'esistenza di uno specifico utente su una piattaforma tramite Selenium.

    Questa funzione utilizza il driver Selenium per accedere alla pagina relativa all'utente specificato e verifica la sua esistenza
    attendendo la visibilità di un elemento indicativo del caricamento corretto della pagina. Se l'elemento viene rilevato entro il
    tempo limite, l'utente è considerato esistente; altrimenti, viene restituito un valore che indica l'assenza dell'utente.

    **Comportamento della funzione**:\n
    1. Utilizza `WebDriverWait` per attendere fino a 120 secondi che la pagina utente sia completamente caricata.\n
    2. Cerca la visibilità di un elemento tramite un selettore XPath per confermare l'esistenza della pagina.\n
    3. Se l'elemento è visibile, restituisce `True`, indicando che l'utente esiste.\n
    4. In caso di timeout, cattura una `TimeoutException`, stampa un messaggio e restituisce `False`.\n

    :param driver: driver selenium per il controllo del browser\n
    :param user: nome dell'utente di cui devo fare il check\n
    :return bool: valore booleano che indica se l'utente esiste o no
    """
    # Verifico che l'utente esista, se non esiste passo alla prossima iterazione
    try:
        # Attendo caricamento pagina
        wait_user = WebDriverWait(driver, 120)

        # Aspettare che un elemento indicativo del completo caricamento della pagina sia visibile
        search_tweets = wait_user.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[1]/div[1]/div/div/div/div/div/div[2]/div/h2')))
        return True
    except TimeoutException:
        logging.exception(f"TimeoutException: utente {user} non trovato..")
        return False


def check_limited_user(driver) -> None:
    """
    Funzione che verifica se un utente è temporaneamente limitato su una piattaforma.

    Questa funzione utilizza Selenium per controllare se, al caricamento della pagina di un utente, è presente un bottone che indica
    che l'accesso al profilo è limitato. Se il bottone è presente, simula la pressione del tasto Invio per rimuovere la limitazione
    e consentire l'accesso al profilo. Se il bottone non è presente, la funzione prosegue senza ulteriori azioni, indicando che
    l'utente non è limitato.

    **Comportamento della funzione**:\n
    1. Cerca la presenza di un elemento rappresentante il bottone di limitazione utilizzando un selettore XPath.\n
    2. Se l'elemento è trovato, simula la pressione del tasto Invio per sbloccare la visualizzazione del profilo.\n
    3. Se l'elemento non è trovato (`NoSuchElementException`), stampa un messaggio e prosegue, poiché l'utente non è limitato.\n

    :param driver: driver selenium per il controllo del browser\n
    :return: Nessun valore ritornato.
    """
    try:
        show_profile_button = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div[2]/div/button')
        show_profile_button.send_keys(Keys.RETURN)
        logging.info("Account limitato..")
    except NoSuchElementException:
        pass


def is_url_in_db(url, collection) -> bool:
    """
    Funzione che verifica se un URL è già presente nel database MongoDB.
    **Funzionamento**: La funzione cerca un documento nella collezione specificata che abbia un campo `url` uguale all'URL fornito. Se il documento esiste, la funzione restituisce `True`, altrimenti restituisce `False`.
    :param url: indiritto URL da cercare nel database.
    :param collection: collezione MongoDB in cui cercare l'URL.
    :return: bool: valore booleano che indica se l'URL è già presente nel database.
    """
    result = collection.find_one({"url": url})  # Sostituisci "tweet_url" con il campo corretto
    return result is not None
