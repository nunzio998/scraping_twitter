"""
Questo script ha lo scopo di definire ed ospitare una serie di funzionalità richiamate dagli altri script.
Alcuni esempi sono:\n
- Gestione interazioni con MongoDB\n
- Parsing dei dati estratti\n
- Procedure di login

Autore: Francesco Pinsone
"""
import json
import pymongo
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


config_data = read_json('/Users/francesco/Documents/Campus Biomedico/2 anno/II Semestre/Tesi Vigimare/python_workspace/src/Telegram_scraping/utils/credentials.json')


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
        logging.info(f"Connesso al database: {client.server_info()['version']}")
    except Exception as e:
        logging.exception(e)

    return client


def disconnect_to_mongo(client):
    """
    Funzione che consente di disconnettersi dal database MongoDB.\n
    :param client: oggetto che rappresenta la connessione al database\n
    :return: None
    """
    logging.info(f"Disconnesso dal database: {client.server_info()['version']}")
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
        logging.info(f"Creata la collezione:{collection_name}")
    else:
        logging.info(f"La collezione esiste già: {collection_name}")

    return db.get_collection(collection_name)


def save_to_mongo(data, collection):
    """
    Funzione per il salvataggio di dati nel database MongoDB.\n
    :param data: dict, dati da salvare\n
    :param collection: oggetto che rappresenta la collezione\n
    :return: None
    """
    collection.insert_one(data)
    logging.info(f"Salvato nel database:{data['id']}")
