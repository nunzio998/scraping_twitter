import json

import pymongo


def read_json(path):
    """
    Funzione per leggere un file JSON.
    :param path:
    :return:
    """
    with open(path, 'r') as file:
        return json.load(file)


config_data = read_json('utils/credentials.json')


# Funzioni MongoDB:
def connect_to_mongo():
    """
    Funzione per connettersi al database.
    :return:
    """
    connection_string = config_data['connection_string']
    client = pymongo.MongoClient(connection_string)
    # Provo a connettermi al database
    try:
        client.admin.command('ping')
        print("Connesso al database: ", client.server_info()["version"])
    except Exception as e:
        print(e)

    return client


def disconnect_to_mongo(client):
    """
    Funzione per disconnettersi dal database.
    :param client:
    :return:
    """
    print("Disconnesso dal database: ", client.server_info()["version"])
    client.close()


def connect_to_mongo_collection(client, collection_name):
    """
    Funzione per connettersi al database e alla collezione.
    :param client:
    :param collection_name:
    :return:
    """
    db = client.get_database(config_data['database'])

    # Verifica se la collezione esiste già
    if collection_name not in db.list_collection_names():
        # Se la collezione non esiste, creala
        db.create_collection(collection_name)
        print("Creata la collezione:", collection_name)
    else:
        print("La collezione esiste già:", collection_name)

    return db.get_collection(collection_name)


def save_to_mongo(data, collection):
    """
    Funzione per salvare i dati nel database.
    :param data:
    :param collection:
    :return:
    """
    collection.insert_one(data)
    print("Salvato nel database: ", data['id'])
