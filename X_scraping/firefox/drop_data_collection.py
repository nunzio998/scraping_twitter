from utils import *


# Mi connetto al database
client = connect_to_mongo()

# Ottengo la lista delle collezioni presenti nel database
collection_list = client.get_database(config_data['database']).list_collection_names()


for collection in collection_list:
    data_coll = connect_to_mongo_collection(client, collection)
    result = data_coll.delete_many({})
    print(f"Eliminati {result.deleted_count} documenti per la collection {collection}")

disconnect_to_mongo(client)