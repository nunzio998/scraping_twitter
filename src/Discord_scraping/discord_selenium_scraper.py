"""
Questo script ha il compito di fare scraping sulla versione web di Discord utilizzando quindi la libreria Python
Selenium. I contenuti estratti vengono poi sottoposti ad un processo di parsing tramite l'utilizzo di BeautifulSoup ed infine salvati su db.\n

Autore: Francesco Pinsone.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
import time
import json

from src.Discord_scraping.utils.utils import read_json, beautifulsoup_analisys, connect_to_mongo, save_to_mongo, \
    connect_to_mongo_collection, \
    disconnect_to_mongo
import logging


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


def discord_login(driver, logging, credentials):
    """
    Funzione che automatizza la procedura di login a Discord.
    :param driver: oggetto instanziato tramite selenium che consente di controllare il browser ed estrarre l'html della pagina.\n
    :param logging: oggetto utilizzato per visualizzare a video i log informativi sull'andamento del processo.\n
    :param credentials: struttura dati che contiene le credenziali dell'utente per l'accesso al proprio profilo Discord.\n
    :return: None\n
    """
    # Loggarsi su Discord
    driver.get('https://discord.com/login')

    # Imposto un'attesa esplicita di massimo 60 secondi
    wait_login = WebDriverWait(driver, 60)

    search_input_login = wait_login.until(EC.visibility_of_element_located((By.ID, 'uid_7')))

    # Controllo la presenza o meno della schermata che specifica la volontà di accedere a Discord col proprio utente o sceglierne un altro.
    # La schermata compare solitamente dopo un elevato numero di esecuzioni. Se è presente simulo la pressione del bottone "Accedi".
    try:
        access_button_field = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[1]/div[1]/div/div/div/section/div[2]/div[2]/div/div/div[3]/button[1]")
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
            logging.info("Tentativo 2: Campo email non trovato..")
            logging.info("Impossibile effettuare l'accesso a Discord.")
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
            logging.info("Tentativo 2: Campo password non trovato..")
            logging.info("Impossibile effettuare l'accesso a Discord.")
            exit(-1)


def discord_scraper():
    """
    Funzione che definisce la metodologia di lavoro dello script. Dopo aver inizializzato il driver selenium per il controllo del browser
    si effettua l'accesso a Discord web. Una volta eseguito il login, per ognuno dei canali e server specificati, si
    scaricano i messaggi presenti e si effettua il parsing con la funzione 'beautifulsoup_analisys' che
    restituisce una lista di messaggi in formato json, il nome del server e il nome del canale da cui sono stati estratti.
    infine i messaggi estratti vengono salvati su un db.\n
    :return: None
    """
    # Configuro il logger
    logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                        format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log

    credentials = read_json("utils/credentials.json")

    # Inizializzo il service selenium
    service = Service('driver/geckodriver')

    # Inizializzo driver  Firefox
    driver = webdriver.Firefox(service=service)

    # Effettuo il login a Discord
    discord_login(driver, logging, credentials)

    time.sleep(1)

    # Cerco la presenza del captcha, se presente lo aggiro.
    try:
        captcha = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[1]/div[5]/div[2]/div/div/div/div[1]/div[4]/div/iframe")
        logging.exception("Captcha presente, carico cookies..")

        # Carico i cookies e faccio il refresh del driver
        load_cookies(driver)
        # driver.refresh()

        # Ripeto la procedura di login
        discord_login(driver, logging, credentials)
        time.sleep(2)
    except NoSuchElementException:
        logging.info("Captcha non presente..")

    time.sleep(1)

    # Mi connetto al database
    client = connect_to_mongo()

    # Ottengo la lista dei target presenti nel database
    targets_collection = connect_to_mongo_collection(client, "discord_target")
    documents = targets_collection.find()
    target_list = [(doc['server_id'], doc['channel_id']) for doc in documents]

    for server_id, channel_id in target_list:
        # carico la pagina del server su cui voglio fare scraping
        search_url = f'https://discord.com/channels/{server_id}/{channel_id}'
        driver.get(search_url)

        # Attendo caricamento pagina
        wait_messages = WebDriverWait(driver, 120)

        # Aspettare che un elemento indicativo del completo caricamento della pagina sia visibile
        search_messages = wait_messages.until(EC.visibility_of_element_located((By.CLASS_NAME, 'panels_a4d4d9')))

        # Numero di volte che vuoi scorrere verso l'alto
        scroll_times = 10

        # Lista per salvare tutti i messaggi, nome del server e nome del canale
        all_messages, server_name, channel_name = beautifulsoup_analisys(driver, scroll_times)

        # Mi connetto alla collezione relativa al server da cui voglio estrarre i dati, se non esiste la creo
        collection = connect_to_mongo_collection(client, server_name)

        for message in all_messages:
            message_to_save = {
                'author': message['author'],
                'date': message['date'],
                'content': message['content'],
                'channel_name': channel_name
            }
            save_to_mongo(message_to_save, collection)

    disconnect_to_mongo(client)
    driver.quit()


if __name__ == "__main__":
    discord_scraper()
