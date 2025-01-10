"""
Questo script fornisce una serie di funzioni utili per la gestione di operazioni di scraping e archiviazione di dati,
con particolare focus sull'integrazione con MongoDB e sull'analisi di contenuti web tramite BeautifulSoup.

Le principali funzionalità includono:
- **Gestione MongoDB**: Connessione al database, creazione e gestione di collezioni, e salvataggio di dati.
- **Analisi HTML**: Utilizzo di BeautifulSoup per estrarre informazioni rilevanti da pagine web, come titolo, snippet e link.
- **Utilità generali**: Lettura di file JSON di configurazione e gestione delle credenziali.

Questo script è progettato per essere modulare e integrabile in altri progetti, fornendo un'architettura robusta e flessibile
per l'elaborazione e l'archiviazione dei dati.

**Autore**: Francesco Pinsone
"""

import json
import pymongo
from bs4 import BeautifulSoup
import logging
import re
from src.DarkWeb_scraping.utils.screenshot_collector import configure_tor_driver, take_screenshot

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


config_data = read_json('/Users/francesco/Documents/Campus Biomedico/2 anno/II Semestre/Tesi/python_workspace/src/DarkWeb_scraping/utils/credentials.json')


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
    :return: Nessun valore restituito.
    """
    collection.insert_one(data)


def beautifulsoup_analisys(response, query):
    """
    Funzione che consente di analizzare il contenuto di una pagina web tramite il modulo BeautifulSoup.\n
    A partire dall'html estrae:\n
    - il titolo che descrive la pagina web\n
    - lo snippet, un piccolo estratto che descrivere la pagina web\n
    In più salva le keywords con cui è composta la query di ricerca utilizzata per ottenere il risultato.\n
    :param response: HTML che rappresenta la risposta della richiesta HTTP\n
    :param query: stringa, query di ricerca\n
    :return: list, lista di dizionari, dove ogni dizionario rappresenta un risultato
    """
    soup = BeautifulSoup(response.text, 'html.parser')

    soup = soup.body

    results = []
    for result in soup.find_all('li', class_='result'):  # scorre la lista degli elementi che risultano dalla ricerca.
        title = result.find('a').text
        # Con l'uso di una regex si estrae il link dalla stringa
        link = re.search(r'https?://[^\s]+', result.find('a')['href']).group(0)
        snippet = result.find('p').text
        # driver = configure_tor_driver()
        # try:
        #     screenshot = take_screenshot(link, driver)
        # except Exception as e:
        #     # logging.exception(e)
        #     screenshot = None
        search_keywords = query.split(' ')
        # results.append({'title': title, 'link': link, 'snippet': snippet, 'screenshot': screenshot,
        #                 'search_keywords': search_keywords})
        results.append({'title': title, 'link': link, 'snippet': snippet, 'search_keywords': search_keywords})
    return results
