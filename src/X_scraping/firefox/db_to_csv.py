"""
Questo script estrae tutti i dati presenti nelle collezioni di un database MongoDB e li esporta in un file CSV.

Il flusso di lavoro include i seguenti passaggi:
1. Si connette al database MongoDB utilizzando la stringa di connessione configurata.
2. Recupera l'elenco di tutte le collezioni nel database.
3. Estrae i dati da ogni collezione e li accumula in un'unica struttura dati.
4. Utilizza la libreria `pandas` per creare un DataFrame contenente tutti i documenti estratti.
5. Esporta il DataFrame in un file CSV nella cartella `data_results`, facilitando l'analisi e l'elaborazione dei dati.

Questa funzionalità è utile per creare un backup dei dati presenti nel database o per analizzare i dati in modo strutturato utilizzando strumenti come Excel, Google Sheets o software di data science come Python o R.

Autore: Francesco Pinsone
"""
import pandas as pd

from src.X_scraping.firefox.utils.utils import *


def export_csv():
    """
    Funzione per esportare i dati presenti nel database MongoDB in un file CSV.

    La funzione esegue le seguenti operazioni:\n
    1. Si connette al database MongoDB utilizzando la stringa di connessione definita nel file di configurazione.\n
    2. Recupera la lista delle collezioni presenti nel database.\n
    3. Per ogni collezione, estrae tutti i documenti e li accumula in una struttura dati.\n
    4. Crea un DataFrame utilizzando la libreria `pandas`, che organizza i dati in formato tabellare.\n
    5. Salva il DataFrame in un file CSV nella cartella `data_results`, rendendo i dati pronti per l'analisi.\n

    La funzione è utile per esportare i dati da MongoDB in un formato facilmente leggibile e analizzabile,
    come CSV, che può essere utilizzato in strumenti di analisi come Excel o software di data science.\n

    :return: Nessun valore ritornato.\n
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
