"""
Questo script ha lo scopo di definire ed ospitare una serie di funzionalità richiamate dagli altri script.
Alcuni esempi sono:\n
- Gestione interazioni con MongoDB\n
- Parsing dei dati estratti\n
- Procedure di login

Autore: Francesco Pinsone
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

interest_groups = ["Killnet", "NoName057(16)", "Lazarus", "DarkHalo", "MustangPanda", "BlackEnergy", "BadMagic",
                   "DarkSide", "LockBit", "DopplePaymer", "RagnarLocker",
                   "REvil", "DragonFly"]

primary_keywords = ["hacker", "cyberwar", "cyber", "energy"]

secondary_keywords = ["italy", "europe", "group", "attack", "threat"]


def read_json(path):
    """
    Funzione per la lettura di file JSON.\n
    :param path: percorso del file JSON\n
    :return: dict, contenuto del file JSON
    """
    with open(path, 'r') as file:
        return json.load(file)


config_data = read_json('/Users/francesco/Documents/Campus Biomedico/2 anno/II Semestre/Tesi/python_workspace/src/X_scraping/chrome/utils/mongo_utils.json')


def x_login(credentials_access, driver_access):
    """
    Funzione che automatizza la procedura di accesso ad X. Prende in input le credenziali d'accesso ('credentials.json) e il driver
    selenium che serve a controllare il browser. Per prima cosa controlla la presenza del campo email, se è presente inserisce
    l'email specificata in 'credentials.json' e simula la pressione del tasto invio sulla tastiera. Prosegue ripetendo lo stesso
    procedimento per i campi username e password.
    :param credentials_access: dict, dizionario di credenziali d'accesso specificate in 'credentials.json'\n
    :param driver_access: driver selenium per il controllo del browser\n
    :return: None
    """
    try:
        email_field = driver_access.find_element(By.XPATH,
                                                 '/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input')
        email_field.send_keys(credentials_access["email"])
        email_field.send_keys(Keys.RETURN)
        time.sleep(2)
    except NoSuchElementException:
        print("Campo email non trovato..")

    # Controllo anche il campo username poiché dopo tanti accessi consecutivi X richiede anche lo username per sicurezza
    try:
        username_field = driver_access.find_element(By.XPATH,
                                                    '/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input')
        username_field.send_keys(credentials_access["username"])
        username_field.send_keys(Keys.RETURN)
        time.sleep(2)
    except NoSuchElementException:
        print("Campo username non trovato..")

    try:
        password_field = driver_access.find_element(By.XPATH,
                                                    '/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input')
        password_field.send_keys(credentials_access["password"])
        password_field.send_keys(Keys.RETURN)
        time.sleep(2)
    except NoSuchElementException:
        print("Campo password non trovato..")


# Funzioni MongoDB:
def connect_to_mongo():
    """
    Funzione che consente di connettersi al database MongoDB.\n
    :return client: oggetto che rappresenta la connessione al database
    """
    connection_string = config_data['connection_string']
    client = pymongo.MongoClient(connection_string)
    # Provo a connettermi al database
    try:
        client.admin.command('ping')
        print("Connesso al database: ", client.server_info()["version"])
    except Exception as e:
        print(e)

    return client


def disconnect_to_mongo(client):
    """
    Funzione che consente di disconnettersi dal database MongoDB.\n
    :param client: oggetto che rappresenta la connessione a mongoDB\n
    :return: None
    """
    print("Disconnesso dal database: ", client.server_info()["version"])
    client.close()


def get_db(client):
    """
    Funzione che ritorna il database MongoDB.
    :param client: oggetto che rappresenta la connessione a mongoDB\n
    :return: oggetto che rappresenta la connessione al db specificato in 'credentials.json'
    """
    return client.get_database(config_data['database'])


def connect_to_mongo_collection(client, collection_name):
    """
    Funzione che consente di connettersi ad una specifica collezione del database MongoDB, oppure di crearla se non esiste.\n
    :param client: oggetto che rappresenta la connessione al database\n
    :param collection_name: stringa, nome della collezione\n
    :return: collection, oggetto che rappresenta la collezione
    """
    db = client.get_database(config_data['database'])

    # Verifica se la collezione esiste già
    if collection_name not in db.list_collection_names():
        # Se la collezione non esiste, creala
        db.create_collection(collection_name)
        print("Creata la collezione:", collection_name)
    else:
        print("La collezione esiste già:", collection_name)

    return db.get_collection(collection_name)


def save_to_mongo(data, collection):
    """
    Funzione per il salvataggio di dati nel database MongoDB.\n
    :param data: dict, dati da salvare\n
    :param collection: oggetto che rappresenta la collezione\n
    :return: None
    """
    collection.insert_one(data)
    print("Salvato nel database: ", data['url'])


def save_user_info_to_mongo(data, collection):
    """
    Funzione che si occupa di il salvataggio di dati, relativi alle info utente, nel database MongoDB.
    Questa funzione viene richiamata dallo script 'user_info_scraper.py'. In tale script non usiamo la funzione
    'save_to_mongo' come visto negli altri script in quanto dopo il salvataggio non visualizziamo più l'url di un
    post salvato ma abbiamo bisogno di visualizzare lo username tag dell'utente di cui stiamo salvando le info nel db.\n
    :param data: dict, dati da salvare\n
    :param collection: oggetto che rappresenta la collezione\n
    :return: None
    """
    collection.insert_one(data)
    print("Salvato nel database: ", data['username_tag'])


# config_data = read_json('mongo_utils.json')

def parse_tweet(tweet):
    """
    Funzione che si occupa di parsare un post e restituirlo in formato json. Questa funzione riceve in input una lista
    di informazioni su uno specifico tweet. Ha lo scopo di parsare il tweet, ovvero organizzare queste informazioni in modo
    opportuno ed estrarne il giusto contenuto informativo. Ogni tweet viene infatti organizzato in un oggetto con la
    seguente struttura:\n
    - 'username': username dell'autore del tweet\n
    - 'tag_username': username_tag dell'autore del tweet\n
    - 'date': data di pubblicazione\n
    - 'scrape_date': data in cui il dato è stato estratto ed elaborato dal codice\n
    - 'content': testo del tweet\n
    - 'reshared': contenuto di un eventuale post ricondiviso\n
    - 'images': immagini contenute nel tweet\n
    - 'videos': video contenuti nel tweet\n
    - 'comments': numero di commenti\n
    - 'reposts': numero di repost\n
    - 'likes': numero di like\n
    - 'views': numero di visualizzazioni\n
    - 'url': url del tweet\n
    :param tweet: list, lista di elementi che che rappresentano il tweet\n
    :return: oggetto con il formato descritto in precedenza\n
    """
    if len(tweet) < 9:
        return None  # Skip invalid posts

    username = tweet[0]

    username_tag = tweet[1]

    data_pubblicazione = tweet[2]

    contenuto = ' '.join(tweet[3].split())

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


def parse_and_save(tweets_to_save, group_name, client):
    """
    Funzione che si occupa di leggere, parsare e salvare i post nel database. Questa funzione viene richiamata nello script
    'tweet_scraper.py'. Alla funzione viene passata una lista che contiene tutte le righe dell'html estratto. Righe che quindi
    rappresentano i vari tweet da estrarre. Per prima cosa con la funzione 'read_posts()' i post vengono raggruppati e divisi
    in base anche al numero di righe. Non avrò più, quindi, una lista con tutte le righe di un file html ma una lista di tweet.
    A questo punto ogni tweet viene sottoposto ad un processo di parsing con la funzione 'parse_post()' e poi salvato a db.\n
    :param tweets_to_save: list, lista che contiene tutte le righe dell'html estratto\n
    :param group_name: str, nome del gruppo target che sto analizzando\n
    :param client: oggetto che rappresenta la connessione a mongoDB\n
    :return: None
    """

    # Connessione alla collezione dati
    collection = connect_to_mongo_collection(client, group_name)

    # Parso ogni post e lo aggiungo al database
    for tweet in tweets_to_save:
        parsed_tweet = parse_tweet(tweet)
        # Salvo il post parsato nel database, se non è None
        if parsed_tweet:
            save_to_mongo(parsed_tweet, collection)


def check_user(driver, user):
    """
    Funzione che effettua un check per verificare l'effettiva esistenza dello specificato utente.\n
    Se l'utente esiste vado avanti (ritorno True) altrimenti continuo col prossimo utente (ritorno False).\n
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
        print(f"TimeoutException: utente {user} non trovato..")
        return False


def check_limited_user(driver):
    """
    Funzione che verifica se l'utente è temporaneamente limitato. In tal caso al caricamento della pagina sarà presente un
    bottone che deve essere premuto per visualizzare correttamente la pagina X del determinato utente. La funzione quindi
    effettua un check sull'effettiva presenza di tale bottone e in caso positivo simula la pressione del tasto invio sulla
    tastiera per premerlo. In caso contrario l'utente non è limitato e si va avanti normalmente.\n
    :param driver: driver selenium per il controllo del browser
    :return None:
    """
    try:
        show_profile_button = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div[2]/div/button')
        show_profile_button.send_keys(Keys.RETURN)
    except NoSuchElementException:
        print("Account non limitato..")
        pass