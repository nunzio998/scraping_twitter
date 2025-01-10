"""
Questo script ha il compito di fare scraping sulla versione web di Discord utilizzando quindi la libreria Python
Selenium. I contenuti estratti vengono poi sottoposti ad un processo di parsing tramite l'utilizzo di BeautifulSoup ed infine salvati su db.\n

Autore: Francesco Pinsone.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver

from src.Discord_scraping.utils.utils import read_json, beautifulsoup_analisys, connect_to_mongo, save_to_mongo, connect_to_mongo_collection, disconnect_to_mongo, login
import logging


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

    conf = read_json("utils/conf.json")

    # Inizializzo il service selenium
    service = Service('driver/geckodriver')

    # Inizializzo driver  Firefox
    driver = webdriver.Firefox(service=service)

    # Effettuo il login a Discord
    login(driver, logging, conf)

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
        scroll_times = conf["scroll_times"]

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
    # TODO: gestire meglio captcha durante l'accesso a Discord web.
