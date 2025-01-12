"""
Questo script permette di eliminare tutti i documenti presenti nelle collezioni di un database MongoDB.

**Funzionalità principali:**\n
1. Si connette al database MongoDB utilizzando la stringa di connessione configurata nel file di configurazione.\n
2. Recupera la lista delle collezioni presenti nel database.\n
3. Per ogni collezione, elimina tutti i documenti in essa contenuti.\n
4. Registra un log dettagliato con il numero di documenti eliminati per ciascuna collezione.\n

L'operazione è irreversibile e rimuove permanentemente tutti i dati dalle collezioni. La funzione è progettata per pulire il database rimuovendo i dati precedentemente raccolti, preparandolo per nuove operazioni o raccolte di dati.

**Autore**: Francesco Pinsone
"""
from src.DarkWeb_scraping.utils.utils import *
import logging


def drop_data():
    """
    Funzione che elimina tutti i documenti presenti nelle collezioni del database MongoDB.

    La funzione esegue i seguenti passaggi:\n
    1. Si connette al database MongoDB utilizzando la stringa di connessione configurata.\n
    2. Recupera la lista delle collezioni presenti nel database.\n
    3. Per ogni collezione, elimina tutti i documenti presenti.\n
    4. Registra un log con il numero di documenti eliminati per ciascuna collezione.\n

    L'operazione è irreversibile e rimuove permanentemente tutti i dati dalle collezioni selezionate,
    che viene esclusa per evitare la perdita dei dati target.\n

    :return: Nessun valore restituito. La funzione si occupa di gestire l'eliminazione e il logging.
    """
    # Configuro il logger
    logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                        format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log

    # Mi connetto al database
    client = connect_to_mongo()

    # Ottengo la lista delle collezioni presenti nel database
    collection_list = client.get_database(config_data['database']).list_collection_names()

    for collection in collection_list:
        data_coll = connect_to_mongo_collection(client, collection)
        result = data_coll.delete_many({})
        logging.info(f"Eliminati {result.deleted_count} documenti per la collection {collection}")

    disconnect_to_mongo(client)


if __name__ == "__main__":
    drop_data()
