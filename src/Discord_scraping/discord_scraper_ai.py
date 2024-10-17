"""
Questo script ha il compito di fare scraping sulla versione web di Discord utilizzando quindi la libreria Python
Selenium. Inoltre avvalendosi di un LLM (Large Language Model) è in grado di effettuare il parsing di una pagina HTML
in modo automatico ed efficace, senza quindi affidarsi esclusivamente all'utilizzo di BeautifulSoup.\n

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
from src.Discord_scraping.utils.utils import read_json, beautifulsoup_analisys, connect_to_mongo, \
    connect_to_mongo_collection, disconnect_to_mongo
import logging
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from bs4 import BeautifulSoup


def discord_ai_scraper():
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

    credentials = read_json("utils/credentials.json")

    # Inizializzo il service selenium
    service = Service('driver/geckodriver')

    # Inizializzo driver  Firefox
    driver = webdriver.Firefox(service=service)

    # Loggarsi manualmente su Discord
    driver.get('https://discord.com/login')

    # Imposto un'attesa esplicita di massimo 60 secondi
    wait_login = WebDriverWait(driver, 60)

    search_input_login = wait_login.until(EC.visibility_of_element_located((By.ID, 'uid_7')))

    # Cerco i campi nei quali far inserire automaticamente le credenziali
    try:
        email_field = driver.find_element(By.ID, 'uid_7')
        email_field.send_keys(credentials["email"])
        time.sleep(1)
    except NoSuchElementException:
        logging.exception("Campo email non trovato..")

    try:
        password_field = driver.find_element(By.ID, 'uid_9')
        password_field.send_keys(credentials["password"])
        password_field.send_keys(Keys.RETURN)
        time.sleep(1)
    except NoSuchElementException:
        logging.exception("Campo password non trovato..")

    # Mi connetto al database
    client = connect_to_mongo()

    # Ottengo la lista dei target presenti nel database
    targets_collection = connect_to_mongo_collection(client, "discord_target")
    documents = targets_collection.find()
    target_list = [(doc['server_id'], doc['channel_id']) for doc in documents]

    prompt_template = PromptTemplate(
        input_variables=["text"],
        template="A partire dal seguente testo vorrei che tu estragga per me una lista di oggetti json ognuno composto da author, date, content e channel_name. La lista e gli oggetti che devi generare per me devono presentarsi nel seguente formato:{text}."
                 "Nota bene: Non voglio un esempio di codice python che automatizzi l'operazione, ma voglio che sia tu ad estrarre i dati in modo che io possa utilizzarli per creare un codice python che automatizzi l'operazione."
    )

    # Formato che gli oggwtti devono avere:
    # [{"author": "", "date": "", "content": "", "channel_name": ""}, {"author": "", "date": "", "content": "", "channel_name": ""}]

    # TODO: Trovare il giusto prompt per l'estrazione dei dati

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

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Lista per salvare tutti i messaggi, nome del server e nome del canale
        all_messages, server_name, channel_name = beautifulsoup_analisys(driver, scroll_times)

        soup = soup.find('div', class_='messagesWrapper_e2e187 group-spacing-16')

        results = soup.text

        # print(results)

        extracted_data = prompt_template | model

        # Eseguo il modello sul testo
        output = extracted_data.invoke({"text": results})

        print(output)

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
    discord_ai_scraper()

    # TODO: gestire captcha durante l'accesso a Discord web.
