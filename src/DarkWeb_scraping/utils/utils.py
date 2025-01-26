"""
Questo script fornisce una serie di funzioni utili per la gestione di operazioni di scraping e archiviazione di dati,
con particolare focus sull'integrazione con MongoDB e sull'analisi di contenuti web tramite BeautifulSoup.

Le principali funzionalità includono:
- **Gestione MongoDB**: Connessione al database, creazione e gestione di collezioni, e salvataggio di dati.
- **Analisi HTML**: Utilizzo di BeautifulSoup per estrarre informazioni rilevanti da pagine web, come titolo, snippet e link.
- **Utilità generali**: Lettura di file JSON di configurazione e gestione delle credenziali.

Questo script è progettato per essere modulare e integrabile in altri progetti, fornendo un'architettura robusta e flessibile
per l'elaborazione e l'archiviazione dei dati.

**Autore**: Francesco Pinsone
"""

import json
import pymongo
from bs4 import BeautifulSoup
import logging
import re
from src.DarkWeb_scraping.utils.screenshot_collector import configure_tor_driver, take_screenshot

# Configuro il logger
logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                    format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log


def read_json(path):
    """
    Funzione per leggere il contenuto di un file JSON e restituirlo come dizionario.

    **Funzionamento**:\n
    1. **Apertura del file**: Apre il file JSON specificato dal percorso `path` in modalità lettura.\n
    2. **Caricamento del contenuto**: Utilizza la funzione `json.load` per caricare il contenuto del file JSON e convertirlo in un oggetto Python (dizionario).\n
    3. **Restituzione dei dati**: Una volta letto il file, la funzione restituisce il dizionario contenente i dati del file JSON.\n

    :param path: str, il percorso del file JSON da leggere.\n
    :return: dict, i dati contenuti nel file JSON, rappresentati come un dizionario Python.
    """
    with open(path, 'r') as file:
        return json.load(file)


config_data = read_json('/Users/francesco/Documents/Campus Biomedico/2 anno/II Semestre/Tesi/python_workspace/src/DarkWeb_scraping/utils/mongo_utils.json')


# Funzioni MongoDB:
def connect_to_mongo():
    """
    Funzione che consente di stabilire una connessione con un database MongoDB utilizzando una stringa di connessione.

    **Passaggi principali**:\n
    1. **Connessione al Database**: Utilizza la stringa di connessione predefinita, configurata nel file di configurazione, per stabilire la connessione con il server MongoDB.\n
    2. **Verifica della Connessione**: Esegue un comando `ping` sul database per verificare se la connessione è attiva. Se la connessione ha successo, viene registrato un log con la versione del server MongoDB.\n
    3. **Gestione degli Errori**: Se si verifica un errore durante il tentativo di connessione, l'errore viene registrato nel log.\n

    **Nota**: Il client MongoDB viene creato utilizzando la libreria `pymongo`, e la connessione viene stabilita utilizzando la stringa di connessione definita nel file di configurazione.\n

    :return: client, oggetto che rappresenta la connessione attiva al database MongoDB.
    """
    connection_string = config_data['connection_string']
    client = pymongo.MongoClient(connection_string)
    # Provo a connettermi al database
    try:
        client.admin.command('ping')
        logging.info("Connesso al database: " + client.server_info()["version"])
    except Exception as e:
        logging.exception(e)

    return client


def disconnect_to_mongo(client):
    """
    Funzione che consente di disconnettersi dal database MongoDB, chiudendo la connessione attiva.

    **Passaggi principali**:\n
    1. **Log della Disconnessione**: La funzione registra un log che indica la disconnessione dal database, includendo la versione del server MongoDB al quale era connesso.\n
    2. **Chiusura della Connessione**: Una volta eseguito il log, la connessione al database viene chiusa, liberando le risorse.\n

    **Nota**: La funzione utilizza il metodo `server_info()` per recuperare informazioni sul server, come la versione, che verranno incluse nel log.\n

    :param client: Oggetto di connessione al database MongoDB. Deve essere un client MongoDB valido, creato con una libreria come `pymongo`.\n
    :return: Nessun valore restituito. La funzione esegue solo l'azione di disconnessione dal database.
    """
    logging.info("Disconnesso dal database: " + client.server_info()["version"])
    client.close()


def connect_to_mongo_collection(client, collection_name):
    """
    Funzione che consente di connettersi a una collezione specifica di MongoDB. Se la collezione non esiste, la funzione la crea automaticamente.

    **Passaggi principali**:\n
    1. **Connessione al Database**: La funzione si connette al database MongoDB utilizzando il client e il nome del database fornito nelle impostazioni.\n
    2. **Verifica e Creazione Collezione**: La funzione verifica se la collezione specificata esiste già nel database. Se non esiste, la funzione la crea.\n
    3. **Restituzione della Collezione**: Una volta verificata o creata la collezione, la funzione restituisce un oggetto che rappresenta la collezione, pronto per operazioni successive.\n

    **Nota**: La funzione assume che la configurazione del database (incluso il nome del database) sia disponibile attraverso un oggetto di configurazione (ad esempio `config_data`).\n

    :param client: Oggetto di connessione al database MongoDB. Deve essere un client MongoDB valido, creato con una libreria come `pymongo`.\n
    :param collection_name: Stringa che rappresenta il nome della collezione a cui ci si vuole connettere o che si vuole creare.\n
    :return: Oggetto che rappresenta la collezione MongoDB. La collezione sarà pronta per l'uso (lettura/scrittura).
    """
    db = client.get_database(config_data['database'])

    # Verifica se la collezione esiste già
    if collection_name not in db.list_collection_names():
        # Se la collezione non esiste, creala
        db.create_collection(collection_name)
        logging.info("Creata la collezione:" + collection_name)
    else:
        logging.info("La collezione esiste già:" + collection_name)

    return db.get_collection(collection_name)


def save_to_mongo(data, collection):
    """
    Funzione che salva i dati in una collezione di MongoDB. La funzione inserisce un singolo documento (dati) nella collezione specificata.

    **Passaggi principali**:\n
    1. **Salvataggio dei dati**: I dati vengono passati come un dizionario (`data`) e vengono inseriti nella collezione MongoDB fornita tramite il metodo `insert_one()`.\n
    2. **Logging**: Viene registrato un messaggio di log che conferma che i dati sono stati salvati nel database.\n

    **Nota**: Questa funzione salva i dati in un'unica operazione e non esegue controlli avanzati (ad esempio, verifica di duplicati o gestione di errori).\n

    :param data: dict, i dati da salvare nel database. Si suppone che siano nel formato appropriato per MongoDB (ad esempio, un dizionario Python).\n
    :param collection: Oggetto che rappresenta la collezione di MongoDB in cui i dati devono essere salvati.\n
    :return: Nessun valore restituito. La funzione esegue solo l'inserimento dei dati.
    """
    logging.info
    collection.insert_one(data)


def is_url_in_db(url, collection):
    """
    Funzione che verifica se un URL è già presente nel database MongoDB.
    **Funzionamento**: La funzione cerca un documento nella collezione specificata che abbia un campo `url` uguale all'URL fornito. Se il documento esiste, la funzione restituisce `True`, altrimenti restituisce `False`.
    :param url: indiritto URL da cercare nel database.
    :param collection: collezione MongoDB in cui cercare l'URL.
    :return: bool: valore booleano che indica se l'URL è già presente nel database.
    """
    result = collection.find_one({"link": url})  # Sostituisci "tweet_url" con il campo corretto
    return result is not None


def beautifulsoup_analisys(response, client, query):
    """
    Funzione che analizza il contenuto di una pagina web tramite BeautifulSoup e estrae informazioni pertinenti dalla risposta HTML.

    **Funzionamento**:\n
    1. **Parsing HTML**: Analizza il contenuto HTML della pagina web fornita tramite il parametro `response` usando BeautifulSoup.\n
    2. **Estrazione dei Dati**: Per ogni risultato della ricerca:\n
        - Estrae il titolo della pagina web.\n
        - Estrae un estratto (snippet) che descrive brevemente la pagina.\n
        - Estrae il link al risultato di ricerca.\n
        - Estrae le parole chiave dalla query di ricerca.\n
    3. **Restituzione dei Risultati**: La funzione restituisce una lista di dizionari, in cui ogni dizionario rappresenta un risultato di ricerca con informazioni come titolo, link, snippet e parole chiave.\n

    **Nota**: La funzione sarà in grado, in futuro, di estrarre anche uno screenshot per ognuna delle pagine web trovate.\n

    :param response: oggetto HTTP, rappresenta la risposta della richiesta alla pagina web (contenente il codice HTML).\n
    :param client: Oggetto di connessione al database MongoDB. Deve essere un client MongoDB valido, creato con una libreria come `pymongo`.\n
    :param query: str, la query di ricerca che ha generato i risultati.

    :return: list, una lista di dizionari dove ogni dizionario contiene:\n
            - `title`: il titolo del risultato.\n
            - `link`: il link al risultato di ricerca.\n
            - `snippet`: una breve descrizione del risultato.\n
            - `search_keywords`: la lista delle parole chiave della query di ricerca.
    """
    collection = connect_to_mongo_collection(client, 'ahmia_results')
    soup = BeautifulSoup(response.text, 'html.parser')

    soup = soup.body

    results = []
    for result in soup.find_all('li', class_='result'):  # scorre la lista degli elementi che risultano dalla ricerca.
        # Con l'uso di una regex si estrae il link dalla stringa
        link = re.search(r'https?://[^\s]+', result.find('a')['href']).group(0)

        if is_url_in_db(link, collection):
            logging.info(f"URL già presente nel database: {link}")
            continue

        title = result.find('a').text

        snippet = result.find('p').text

        # driver = configure_tor_driver()
        # try:
        #     screenshot = take_screenshot(link, driver)
        # except Exception as e:
        #     # logging.exception(e)
        #     screenshot = None

        search_keywords = query.split(' ')

        # results.append({'title': title, 'link': link, 'snippet': snippet, 'screenshot': screenshot,
        #                 'search_keywords': search_keywords})

        results.append({'title': title, 'link': link, 'snippet': snippet, 'search_keywords': search_keywords})
    return results
