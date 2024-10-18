"""
Questo script permette di eliminare tutti i documenti presenti nelle collezioni del database.

Autore: Francesco Pinsone
"""
from src.Telegram_scraping.utils.utils import *


def drop_data():
    """
    Funzione per eliminare tutti i documenti presenti nelle collezioni del database.\n
    :return: None
    """
    # Mi connetto al database
    client = connect_to_mongo()

    # Ottengo la lista delle collezioni presenti nel database
    collection_list = client.get_database(config_data['database']).list_collection_names()

    for collection in collection_list:
        data_coll = connect_to_mongo_collection(client, collection)
        result = data_coll.delete_many({})
        print(f"Eliminati {result.deleted_count} documenti per la collection {collection}")

    disconnect_to_mongo(client)


if __name__ == "__main__":
    drop_data()