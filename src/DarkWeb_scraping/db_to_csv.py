"""
Questo script permette di esportare i dati presenti nel database in un file csv. I dati vengono estratti da tutte le collezioni presenti nel database e vengono salvati in un unico file csv.

Autore: Francesco Pinsone
"""
import pandas as pd

from src.DarkWeb_scraping.utils.utils import *


def export_csv():
    """
    Funzione per esportare i dati presenti nel database in un file csv.\n
    :return: None
    """
    # Mi connetto al database
    client = connect_to_mongo()

    # Ottengo la lista delle collezioni presenti nel database
    collection_list = client.get_database(config_data['database']).list_collection_names()

    data = ()

    for collection in collection_list:
        data_coll = connect_to_mongo_collection(client, collection)

        data_tmp = list(data_coll.find())
        data = data + tuple(data_tmp)

    df = pd.DataFrame(data)
    df.to_csv('data_results/data.csv', index=False)


if __name__ == "__main__":
    export_csv()
