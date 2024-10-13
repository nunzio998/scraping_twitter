"""
Questo script permette di fare scraping del motore di ricerca Ahmia, uno dei motori di ricerca per il dark web. La ricerca viene effettuata per parole chiave e i risultati che produce vengono
salvati in un database MongoDB. Per fare scraping di Ahmia è necessario utilizzare Tor, quindi è necessario avere un server Tor in esecuzione sul proprio computer. Inoltre, è necessario avere
installato il browser Tor e configurare il proxy per le richieste HTTP.

Autore: Francesco Pinsone
"""

import requests
from src.DarkWeb_scraping.utils.utils import connect_to_mongo, connect_to_mongo_collection, save_to_mongo, disconnect_to_mongo, beautifulsoup_analisys
import logging


# Funzione per cercare in Ahmia
def search_ahmia(query):
    """
    Funzione per cercare in Ahmia, uno dei motori di ricerca per il dark web. La funzione prende in input una query di ricerca e ritorna i risultati sotto forma di
    lista di dizionari, dove ogni dizionario rappresenta un risultato.
    :param query: stringa, query di ricerca
    :return: list, lista di dizionari, dove ogni dizionario rappresenta un risultato
    """
    # URL di Ahmia versione onion
    url = f'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/search/?q={query}'

    try:
        response = session.get(url)
        response.raise_for_status()  # Verifica se la richiesta è andata a buon fine
    except requests.exceptions.RequestException as e:
        print(f"Errore di connessione: {e}")
        return []

    res = beautifulsoup_analisys(response, query)

    return res


if __name__ == "__main__":
    # Configuro il logger
    logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                        format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log

    proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }

    session = requests.Session()
    session.proxies.update(proxies)

    client = connect_to_mongo()

    # Esempio di ricerca
    query = 'hacker attack energy infrastructure'
    results = search_ahmia(query)

    collection = connect_to_mongo_collection(client, "ahmia_results")

    # Stampa dei risultati
    for result in results:
        logging.info(f"Link: {result['link']}")

        json_result = {
            'title': result['title'],
            'link': result['link'],
            'snippet': result['snippet'],
            'search_keywords': result['search_keywords']
        }
        save_to_mongo(json_result, collection)

    disconnect_to_mongo(client)