"""
Questo script esegue il processo di scraping sul motore di ricerca Ahmia, che è una risorsa per esplorare il dark web. Utilizzando la rete Tor per garantire l'anonimato, la funzione principale
effettua una ricerca tramite una query di parole chiave e salva i risultati nel database MongoDB. Questo processo permette di raccogliere informazioni provenienti dal dark web in modo sicuro e
anonimo, archiviandole per ulteriori analisi o monitoraggi.

**Passaggi principali**:\n
1. **Connessione a Tor**: Configurazione dei proxy SOCKS5 per permettere la connessione alla rete Tor.\n
2. **Connessione a MongoDB**: Connessione al database MongoDB per il salvataggio dei dati estratti.\n
3. **Esecuzione della ricerca**: Utilizzo della funzione `search_ahmia()` per inviare una query di ricerca su Ahmia.\n
4. **Salvataggio dei risultati**: I risultati vengono analizzati e salvati nel database MongoDB.\n
5. **Disconnessione dal database**: La connessione a MongoDB viene chiusa una volta completato il salvataggio dei dati.\n

**Requisiti**:\n
- È necessario avere un server Tor in esecuzione sul computer e configurato correttamente.\n
- MongoDB deve essere installato e configurato per l'archiviazione dei risultati.\n

**Autore**: Francesco Pinsone
"""

import requests
from src.DarkWeb_scraping.utils.utils import connect_to_mongo, connect_to_mongo_collection, save_to_mongo, disconnect_to_mongo, beautifulsoup_analisys, read_json
import logging


# Funzione per cercare in Ahmia
def search_ahmia(session, query):
    """
    Funzione per effettuare una ricerca su Ahmia, un motore di ricerca del dark web. Questa funzione invia una query a Ahmia
    e restituisce i risultati sotto forma di una lista di dizionari, in cui ogni dizionario rappresenta un risultato.\n

    **Passaggi principali**:\n
    1. **Costruzione dell'URL**: Combina l'URL di Ahmia (versione onion) con la query di ricerca specificata.\n
    2. **Invio della Richiesta**: Utilizza la sessione configurata con proxy Tor per inviare una richiesta HTTP al motore di ricerca.\n
    3. **Gestione degli Errori**: Verifica eventuali errori di connessione o nella richiesta e, in caso di problemi, restituisce una lista vuota.\n
    4. **Analisi dei Risultati**: Utilizza la funzione `beautifulsoup_analisys()` per analizzare la risposta HTML e estrarre i dati rilevanti.\n

    :param query: stringa, query di ricerca\n
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


def darkweb_scraper():
    """
    Questa funzione rappresenta il punto di partenza per eseguire uno scraping sul dark web. Utilizza il proxy Tor
    per garantire l'anonimato e la navigazione sicura. La funzione include i seguenti passaggi principali:

    1. **Configurazione dei Proxy**: Imposta i proxy SOCKS5 per abilitare la navigazione su Tor.\n
    2. **Connessione al Database MongoDB**: Stabilisce una connessione al database per archiviare i dati estratti.\n
    3. **Esecuzione della Ricerca**: Utilizza la funzione 'search_ahmia()' per cercare contenuti specifici sul dark web
       in base alla query fornita (es. "hacker attack energy infrastructure").\n
    4. **Salvataggio dei Risultati**: Analizza i risultati della ricerca, li formatta come JSON, e li salva nella collezione
       appropriata del database.\n
    5. **Disconnessione dal Database**: Garantisce la chiusura della connessione al database al termine delle operazioni.\n

    Questa funzione è progettata per gestire automaticamente la raccolta e l'archiviazione dei dati provenienti dal dark web,
    rendendola ideale per progetti di analisi o monitoraggio.
    :return: Nessun valore restituito.
    """
    # Configuro il logger
    logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                        format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log

    conf = read_json("/Users/francesco/Documents/Campus Biomedico/2 anno/II Semestre/Tesi/python_workspace/src/DarkWeb_scraping/utils/conf.json")

    proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }

    session = requests.Session()
    session.proxies.update(proxies)

    client = connect_to_mongo()

    results = search_ahmia(session, conf['target_query'])

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


if __name__ == "__main__":
    darkweb_scraper()
