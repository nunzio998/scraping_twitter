"""
Questo script ha il compito di fare scraping sulla versione web di Discord utilizzando quindi la libreria Python
Selenium. Inoltre avvalendosi di un LLM (Large Language Model) è in grado di effettuare il parsing di una pagina HTML
in modo automatico ed efficace, senza quindi affidarsi esclusivamente all'utilizzo di BeautifulSoup. Quest'ultima parte,
tuttavia, richiede l'utilizzo di un modello più performante di quello a disposizione. Sarà quindi completata insieme ad
altri sviluppi futuri.\n

Autore: Francesco Pinsone.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium import webdriver
import time
from src.Discord_scraping.utils.utils import read_json, beautifulsoup_analisys, connect_to_mongo, \
    connect_to_mongo_collection, disconnect_to_mongo, scroll_up
import logging
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from bs4 import BeautifulSoup
from openai import OpenAI
import json


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
    # Loggarsi su Discord
    driver.get('https://discord.com/login')

    # Imposto un'attesa esplicita di massimo 20 secondi
    wait_login = WebDriverWait(driver, 20)

    search_input_login = wait_login.until(EC.visibility_of_element_located((By.ID, 'uid_7')))


    # Controllo la presenza o meno della schermata che specifica la volontà di accedere a Discord col proprio utente
    # o sceglierne un altro. La schermata compare solitamente dopo un elevato numero di esecuzioni. Se è presente
    # simulo la pressione del bottone "Accedi".
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
    Funzione che effettua un check sulla presenza di test captcha dopo che lo script ha tentato la procedura di login. Inizialmente se la presenza
    di un captcha viene rilevata la funzione tenta di caricare nel driver di Firefox i cookies di una sessione in cui l'accesso è andato a buon fine.
    Questo è possibile con l'esecuzione dello script 'extract_cookies.py'. Nel caso in cui questo approccio non dovesse bastare la funzione permette
    all'utente di risolvere manualmente il test per poi procedere con l'estrazione dei dati.\n
    :param driver: oggetto instanziato tramite selenium che consente di controllare il browser ed estrarre l'html della pagina.\n
    :param logging: oggetto utilizzato per visualizzare a video i log informativi sull'andamento del processo.\n
    :param credentials: struttura dati che contiene le credenziali dell'utente per l'accesso al proprio profilo Discord.\n
    :return: None\n
    """
    # Cerco la presenza del captcha, se presente cerco di bypassarlo.
    try:
        captcha = driver.find_element(By.XPATH,
                                      "/html/body/div[2]/div[2]/div[1]/div[5]/div[2]/div/div/div/div[1]/div[4]/div/iframe")
        logging.exception("Captcha presente, carico cookies..")

        # Carico i cookies e faccio il refresh del driver
        load_cookies(driver)
        driver.refresh()

        # Ripeto la procedura di login
        discord_login(driver, logging, credentials)
        time.sleep(1)
    except NoSuchElementException:
        logging.info("Captcha non presente..")

    # Se il captcha è ancora presente vuol dire che non sono riuscito a bypassarlo, quindi lo faccio risolvere all'utente.
    try:
        captcha = driver.find_element(By.XPATH,
                                      "/html/body/div[2]/div[2]/div[1]/div[5]/div[2]/div/div/div/div[1]/div[4]/div/iframe")
        logging.exception("Captcha ancora presente, risolvere manualmente..")

        input("Premi ENTER dopo aver risolto il captcha..")

        # discord_login(driver, logging, credentials)
        time.sleep(1)
    except NoSuchElementException:
        logging.info("Captcha non presente, procedura di login terminata..")


def discord_chatgpt_scraper():
    # TODO: Da sviluppare quando si avrà accesso all'API di Chatgpt.
    pass


def discord_ollama_scraper():
    """
    Funzione che definisce la metodologia di lavoro dello script. Dopo aver inizializzato LLM e driver per il controllo del browser
    si effettua l'accesso a Discord web. Una volta eseguito il login, per ognuno dei canali e server specificati, si
    scaricano i messaggi presenti e si effettua il parsing tramite LLM. I risultati verranno poi salvati su db.\n
    :return: None
    """
    model = OllamaLLM(model='llama3.1')

    # Configuro il logger
    logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                        format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log

    conf = read_json("utils/conf.json")

    # Inizializzo il service selenium
    service = Service('driver/geckodriver')

    # Inizializzo driver  Firefox
    driver = webdriver.Firefox(service=service)

    # Procedura di login
    login(driver, logging, conf)

    # Mi connetto al database
    client = connect_to_mongo()

    # Ottengo la lista dei target presenti nel database
    targets_collection = connect_to_mongo_collection(client, "discord_target")
    documents = targets_collection.find()
    target_list = [(doc['server_id'], doc['channel_id']) for doc in documents]

    prompt_template = PromptTemplate(
        input_variables=["text"],
        template="{text}. Da questo testo estrai una lista di messaggi in formato json. Ogni messaggio è composto dai campi: author, date, content e channel_name (che lascerai vuoto). Non scrivere in output nulla oltre la lista di oggetti json."
    )
    # TODO: Trovare il giusto prompt per l'estrazione dei dati

    for server_id, channel_id in target_list:
        # carico la pagina del server su cui voglio fare scraping
        search_url = f'https://discord.com/channels/{server_id}/{channel_id}'
        driver.get(search_url)

        # Attendo caricamento pagina
        wait_messages = WebDriverWait(driver, 60)

        # Aspettare che un elemento indicativo del completo caricamento della pagina sia visibile
        search_messages = wait_messages.until(EC.visibility_of_element_located((By.CLASS_NAME, 'panels_a4d4d9')))

        # Numero di volte che vuoi scorrere verso l'alto
        scroll_times = conf['scroll_times']

        scroll_up(driver, scroll_times)

        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        soup = soup.body

        server_name = soup.find('h2', class_='defaultColor_a595eb lineClamp1_a595eb text-md/semibold_dc00ef defaultColor_e42ec6 name_fd6364').text
        channel_name = soup.find('h1', class_='defaultColor_a595eb heading-md/semibold_dc00ef defaultColor_e42ec6 title_fc4f04').text.split(": ")[1]

        soup = soup.main

        ol_messages = soup.find("ol", class_="scrollerInner_e2e187")

        extracted_data = prompt_template | model

        # Eseguo il modello sul testo
        output = extracted_data.invoke({"text": ol_messages.text})

        print(f"Risposta Ollama:\n{output}")

        # # Mi connetto alla collezione relativa al server da cui voglio estrarre i dati, se non esiste la creo
        # collection = connect_to_mongo_collection(client, server_name)
        #
        # for message in all_messages:
        #     message_to_save = {
        #         'author': message['author'],
        #         'date': message['date'],
        #         'content': message['content'],
        #         'channel_name': channel_name
        #     }
        #     save_to_mongo(message_to_save, collection)

    disconnect_to_mongo(client)
    driver.quit()


if __name__ == "__main__":
    discord_ollama_scraper()
    # TODO: gestire meglio captcha durante l'accesso a Discord web.
