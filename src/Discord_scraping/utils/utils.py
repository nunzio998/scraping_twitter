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
import pymongo
from bs4 import BeautifulSoup
from selenium.common import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import logging

# Configuro il logger
logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                    format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log


def read_json(path):
    """
    Funzione per la lettura di file JSON.\n
    :param path: percorso del file JSON\n
    :return: dict, contenuto del file JSON
    """
    with open(path, 'r') as file:
        return json.load(file)


config_data = read_json('/Users/francesco/Documents/Campus Biomedico/2 anno/II Semestre/Tesi/python_workspace/src/Discord_scraping/utils/conf.json')


# Funzioni MongoDB:
def connect_to_mongo():
    """
    Funzione che consente di connettersi al database MongoDB.\n
    :return: client, oggetto che rappresenta la connessione al database
    """
    connection_string = config_data['connection_string']
    client = pymongo.MongoClient(connection_string)
    # Provo a connettermi al database
    try:
        client.admin.command('ping')
        logging.info("Connesso al database: " + client.server_info()["version"])
    except Exception as e:
        logging.exception(e)

    return client


def disconnect_to_mongo(client):
    """
    Funzione che consente di disconnettersi dal database MongoDB.\n
    :param client: oggetto che rappresenta la connessione al database\n
    :return: None
    """
    logging.info("Disconnesso dal database: " + client.server_info()["version"])
    client.close()


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
        logging.info("Creata la collezione:" + collection_name)
    else:
        logging.info("La collezione esiste già:" + collection_name)

    return db.get_collection(collection_name)


def save_to_mongo(data, collection):
    """
    Funzione per il salvataggio di dati nel database MongoDB.\n
    :param data: dict, dati da salvare\n
    :param collection: oggetto che rappresenta la collezione\n
    :return: None
    """
    collection.insert_one(data)
    logging.info(f"Salvato nel db: {data}")


def beautifulsoup_analisys(driver, scroll_times):
    """
    Funzione che consente di analizzare il contenuto di una pagina web tramite il modulo BeautifulSoup.\n
    :param driver: oggetto instanziato tramite selenium che consente di controllare il browser ed estrarre l'html della pagina.\n
    :param scroll_times: numero di esecuzioni di scroll up della chat per caricare più messaggi.\n
    :return: list: lista dei messaggi.\n
            str: nome del server.\n
            str: nome del canale.
    """
    all_messages = []
    server_name = None
    channel_name = None

    # Scorri verso l'alto per caricare più messaggi e salva i nuovi messaggi
    for _ in range(scroll_times):
        scroll_up(driver, 1)

        # Estraggo HTML pagina con BeautifulSoup
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        soup = soup.body

        # Trova nome server e nome canale
        server_name = soup.find('h2', class_='defaultColor_a595eb lineClamp1_a595eb text-md/semibold_dc00ef defaultColor_e42ec6 name_fd6364').text
        channel_name = soup.find('h1', class_='defaultColor_a595eb heading-md/semibold_dc00ef defaultColor_e42ec6 title_fc4f04').text.split(": ")[1]

        # Trova tutti i messaggi
        messages = soup.find_all('div', class_='contents_f9f2ca')

        for message in messages:
            # Trovo autore e data. Se non trovo l'autore vuol dire che l'autore è lo stesso del messaggio precedente quindi resta invariato
            if message.find('span', class_='username_f9f2ca desaturateUserColors_c7819f clickable_f9f2ca'):
                author = message.find('span', class_='username_f9f2ca desaturateUserColors_c7819f clickable_f9f2ca').text

            timestamp = message.find('time')['datetime']

            # Trovo il contenuto del messaggio
            content = message.find('div', class_='markup_f8f345 messageContent_f9f2ca').text
            # Se la stringa è vuota, salta il messaggio (non lo salva)
            if re.fullmatch(r'\n*', content):
                continue
            all_messages.append({'author': author, 'date': timestamp, 'content': content})

    return all_messages, server_name, channel_name


# Funzione per scorrere verso l'alto e caricare più messaggi
def scroll_up(driver, times):
    """
    Funzione per scorrere verso l'alto e caricare più messaggi.\n
    :param driver: oggetto instanziato tramite selenium che consente di controllare il browser ed estrarre l'html della pagina.\n
    :param times: numero di esecuzioni di scroll up della chat per caricare più messaggi.\n
    :return: None
    """
    for _ in range(times):
        page = driver.find_element(By.TAG_NAME, 'html')
        page.send_keys(Keys.PAGE_UP)
        time.sleep(2)  # Aspetta che i messaggi vengano caricati


def load_cookies(driver, cookies_path="utils/cookies.json"):
    """
    Funzione che carica i cookies salvati da un file JSON e li aggiunge alla sessione Selenium.\n
    :param driver: oggetto instanziato tramite selenium che consente di controllare il browser ed estrarre l'html della pagina.\n
    :param cookies_path: path del file json che contiene i cookies di sessione per superare il captcha.\n
    :return: None\n
    """
    with open(cookies_path, "r") as file:
        cookies = json.load(file)
    for cookie in cookies:
        driver.add_cookie(cookie)


def login(driver, logging, credentials):
    """
    Funzione che fa partire la procedura di login e successivamente richiama un check verificare la presenza di captcha.
    :param driver: oggetto instanziato tramite selenium che consente di controllare il browser ed estrarre l'html della pagina.\n
    :param logging: oggetto utilizzato per visualizzare a video i log informativi sull'andamento del processo.\n
    :param credentials: struttura dati che contiene le credenziali dell'utente per l'accesso al proprio profilo Discord.\n
    :return: None\n
    """
    # Effettuo il login a Discord
    discord_login(driver, logging, credentials)

    time.sleep(1)

    # Cerco la presenza di captcha, se ci sono provo a bypassarli.
    check_captcha(driver, logging, credentials)


def discord_login(driver, logging, credentials):
    """
    Funzione che automatizza la procedura di login a Discord.
    :param driver: oggetto instanziato tramite selenium che consente di controllare il browser ed estrarre l'html della pagina.\n
    :param logging: oggetto utilizzato per visualizzare a video i log informativi sull'andamento del processo.\n
    :param credentials: struttura dati che contiene le credenziali dell'utente per l'accesso al proprio profilo Discord.\n
    :return: None\n
    """
    # Caricamento pagina di login discord
    driver.get('https://discord.com/login')

    # Imposto un'attesa esplicita di massimo 60 secondi
    wait_login = WebDriverWait(driver, 60)

    search_input_login = wait_login.until(EC.visibility_of_element_located((By.ID, 'uid_7')))

    # Controllo la presenza o meno della schermata che specifica la volontà di accedere a Discord col proprio utente o sceglierne un altro.
    # La schermata compare solitamente dopo un elevato numero di esecuzioni. Se è presente simulo la pressione del bottone "Accedi".
    try:
        access_button_field = driver.find_element(By.XPATH,
                                                  "/html/body/div[1]/div[2]/div[1]/div[1]/div/div/div/section/div[2]/div[2]/div/div/div[3]/button[1]")
        access_button_field.send_keys(Keys.RETURN)
        time.sleep(2)
    except NoSuchElementException:
        logging.info("Schermata di selezione utente assente..")

    # Cerco i campi nei quali far inserire automaticamente le credenziali
    try:
        email_field = driver.find_element(By.ID, 'uid_7')
        email_field.send_keys(credentials["email"])
        time.sleep(2)
    except NoSuchElementException:
        logging.info("Tentativo 1: Campo email non trovato..")
        try:
            email_field = driver.find_element(By.ID, 'uid_8')
            email_field.send_keys(credentials["email"])
            time.sleep(2)
        except NoSuchElementException:
            logging.info("Tentativo 2: Campo email non trovato, Impossibile effettuare l'accesso a Discord..")
            driver.quit()
            exit(-1)

    try:
        password_field = driver.find_element(By.ID, 'uid_9')
        password_field.send_keys(credentials["password"])
        password_field.send_keys(Keys.RETURN)
        time.sleep(2)
    except NoSuchElementException:
        logging.info("Tentativo 1: Campo password non trovato..")
        try:
            password_field = driver.find_element(By.ID, 'uid_10')
            password_field.send_keys(credentials["password"])
            password_field.send_keys(Keys.RETURN)
            time.sleep(2)
        except NoSuchElementException:
            logging.info("Tentativo 2: Campo password non trovato, Impossibile effettuare l'accesso a Discord..")
            driver.quit()
            exit(-1)


def check_captcha(driver, logging, credentials):
    """
    Funzione che effettua un check sulla presenza di test captcha dopo che lo script ha tentato la procedura di login. Per ora se un captcha viene rilevato si
    rimanda all'utente la risoluzione dello stesso prima di continuare.\n
    Gl isviluppi futuri prevedono che: inizialmente se la presenza di un captcha viene rilevata la funzione tenta di caricare nel driver di Firefox i cookies di una sessione in cui l'accesso è andato a buon fine.
    Questo è possibile con l'esecuzione dello script 'extract_cookies.py'. Nel caso in cui questo approccio non dovesse bastare la funzione permette
    all'utente di risolvere manualmente il test per poi procedere con l'estrazione dei dati.\n
    :param driver: oggetto instanziato tramite selenium che consente di controllare il browser ed estrarre l'html della pagina.\n
    :param logging: oggetto utilizzato per visualizzare a video i log informativi sull'andamento del processo.\n
    :param credentials: struttura dati che contiene le credenziali dell'utente per l'accesso al proprio profilo Discord.\n
    :return: None\n
    """
    # # Cerco la presenza del captcha, se presente cerco di bypassarlo.
    # try:
    #     captcha = driver.find_element(By.XPATH,
    #                                   "/html/body/div[2]/div[2]/div[1]/div[5]/div[2]/div/div/div/div[1]/div[4]/div/iframe")
    #     logging.info("Captcha presente, carico cookies..")
    #
    #     # Carico i cookies e faccio il refresh del driver
    #     load_cookies(driver)
    #     driver.refresh()
    #
    #     # Comando con cui si cerca di rimuovere il test captcha dal DOM.
    #     driver.execute_script("document.getElementById('captcha').style.display = 'none';")
    #
    #     # Ripeto la procedura di login
    #     discord_login(driver, logging, credentials)
    #     time.sleep(1)
    # except NoSuchElementException:
    #     logging.info("Captcha non presente..")
    #
    # # Se il captcha è ancora presente vuol dire che non sono riuscito a bypassarlo, quindi lo faccio risolvere all'utente.
    # try:
    #     captcha = driver.find_element(By.XPATH,
    #                                   "/html/body/div[2]/div[2]/div[1]/div[5]/div[2]/div/div/div/div[1]/div[4]/div/iframe")
    #     logging.info("Captcha ancora presente, risolvere manualmente..")
    #
    #     input("Premi ENTER dopo aver risolto il captcha..")
    #
    #     discord_login(driver, logging, credentials)
    #     time.sleep(1)
    # except NoSuchElementException:
    #     logging.info("Captcha non presente, procedura di login terminata..")

    try:
        captcha = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[1]/div[5]/div[2]/div/div/div/div[1]/div[4]/div/iframe")
        logging.info("Captcha presente, risolvere manualmente e premere invio dopo la risoluzione..")

        input("Premi ENTER dopo aver risolto il captcha..")
        time.sleep(1)
    except NoSuchElementException:
        logging.info("Captcha non presente, procedura di login terminata..")


