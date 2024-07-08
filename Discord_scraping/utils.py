import json
import re
from datetime import datetime
import pymongo


def read_json(path):
    with open(path, 'r') as file:
        return json.load(file)


config_data = read_json('utils/credentials.json')


# Funzioni MongoDB:
def connect_to_mongo():
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
    print("Disconnesso dal database: ", client.server_info()["version"])
    client.close()


def connect_to_mongo_collection(client, collection_name):
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
    collection.insert_one(data)
    print("Salvato nel database: ", data['id'])
