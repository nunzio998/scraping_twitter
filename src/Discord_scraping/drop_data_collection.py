"""
Questo script permette di eliminare tutti i documenti presenti nelle collezioni del database.

Autore: Francesco Pinsone
"""
from src.Discord_scraping.utils.utils import *
import logging


def drop_data():
    """
    Funzione per eliminare tutti i documenti presenti nelle collezioni del database.\n
    :return: None
    """
    # Configuro il logger
    logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                        format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log

    # Mi connetto al database
    client = connect_to_mongo()

    # Ottengo la lista delle collezioni presenti nel database
    collection_list = client.get_database(config_data['database']).list_collection_names()

    for collection in collection_list:
        # Salto la lista dei target
        if collection == "discord_target":
            continue
        data_coll = connect_to_mongo_collection(client, collection)
        result = data_coll.delete_many({})
        logging.info(f"Eliminati {result.deleted_count} documenti per la collection {collection}")

    disconnect_to_mongo(client)


if __name__ == "__main__":
    drop_data()
