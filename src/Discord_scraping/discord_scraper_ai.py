"""
Questo script ha il compito di fare scraping sulla versione web di Discord utilizzando quindi la libreria Python
Selenium. Inoltre avvalendosi di un LLM (Large Language Model) è in grado di effettuare il parsing di una pagina HTML
in modo automatico ed efficace, senza quindi affidarsi esclusivamente all'utilizzo di BeautifulSoup. Quest'ultima parte,
tuttavia, richiede l'utilizzo di un modello più performante di quello a disposizione. Sarà quindi completata insieme ad
altri sviluppi futuri.\n

Autore: Francesco Pinsone.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from src.Discord_scraping.utils.utils import read_json, connect_to_mongo, connect_to_mongo_collection, disconnect_to_mongo, scroll_up, login
import logging
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from bs4 import BeautifulSoup

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
