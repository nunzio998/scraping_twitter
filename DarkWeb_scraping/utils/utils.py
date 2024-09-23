import json
import pymongo
from bs4 import BeautifulSoup
import logging

# Configuro il logger
logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                    format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log


def read_json(path):
    with open(path, 'r') as file:
        return json.load(file)


config_data = read_json('utils/credentials.json')


# Funzioni MongoDB:
def connect_to_mongo():
    """
    Funzione che consente di connettersi al database MongoDB.
    :return:
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
    Funzione che consente di disconnettersi dal database MongoDB.
    :param client:
    :return:
    """
    logging.info("Disconnesso dal database: " + client.server_info()["version"])
    client.close()


def connect_to_mongo_collection(client, collection_name):
    """
    Funzione che consente di connettersi ad una specifica collezione del database MongoDB, oppure di crearla se non esiste.
    :param client:
    :param collection_name:
    :return:
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
    Funzione per il salvataggio di dati nel database MongoDB.
    :param data:
    :param collection:
    :return:
    """
    collection.insert_one(data)


def beautifulsoup_analisys(response, query):
    """
    Funzione che consente di analizzare il contenuto di una pagina web tramite il modulo BeautifulSoup.
    :param response:
    :param query:
    :return:
    """
    soup = BeautifulSoup(response.text, 'html.parser')

    soup = soup.body

    results = []
    for result in soup.find_all('li', class_='result'):  # scorre la lista degli elementi che risultano dalla ricerca.
        title = result.find('a').text
        link = result.find('a')['href']
        snippet = result.find('p').text
        search_keywords = query.split(' ')
        results.append({'title': title, 'link': link, 'snippet': snippet, 'search_keywords': search_keywords})

    return results
