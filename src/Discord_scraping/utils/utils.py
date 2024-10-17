import json
import re
import time
import pymongo
from bs4 import BeautifulSoup
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


config_data = read_json('/Users/francesco/Documents/Campus Biomedico/2 anno/II Semestre/Tesi Vigimare/python_workspace/src/Discord_scraping/utils/credentials.json')


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

    # Scorri verso l'alto per caricare più messaggi e salva i nuovi messaggi
    for _ in range(scroll_times):
        scroll_up(driver, 1)

        # Estraggo HTML pagina con BeautifulSoup
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        soup = soup.body

        # Trova nome server e nome canale
        server_name = soup.find('h2', class_='defaultColor_a595eb lineClamp1_a595eb text-md/semibold_dc00ef defaultColor_e42ec6 name_fd6364').text
        channel_name = soup.find('h1', class_='defaultColor_a595eb heading-md/semibold_dc00ef defaultColor_e9e35f title_fc4f04').text.split(': ')[1]

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
