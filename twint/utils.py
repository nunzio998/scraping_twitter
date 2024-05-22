import json
import pymongo


def read_json(path):
    with open(path, 'r') as file:
        return json.load(file)


def dict_to_json(dict_data):
    return json.dumps(dict_data)


def connect_to_mongo():
    connection_string = config_data['connection_string']
    client_tmp = pymongo.MongoClient(connection_string)
    # Provo a connettermi al database
    try:
        client_tmp.admin.command('ping')
        print("Connesso al database: ", client_tmp.server_info()["version"])
    except Exception as e:
        print(e)

    return client_tmp


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
    for tweet in data:
        collection.insert_one(tweet)


config_data = read_json('data/mongo_utils.json')
