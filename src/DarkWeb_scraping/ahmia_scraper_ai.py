"""
Questo script si occupa di effettuare scraping su Ahmia, uno dei motori di ricerca per il dark web, e di estrarre i risultati ottenuti. In questo caso l'html che viene estratto durante lo scraping
viene parsato avvalendosi di un LLM (Large Language Model) per estrarre informazioni utili dai risultati ottenuti.

Autore: Francesco Pinsone
"""
import requests
import logging
from bs4 import BeautifulSoup
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate


# Funzione per cercare in Ahmia
def search_ahmia(query):
    """
    Funzione per cercare in Ahmia, uno dei motori di ricerca per il dark web. La funzione prende in input una query di ricerca e ritorna i risultati sotto forma di
    lista di dizionari, dove ogni dizionario rappresenta un risultato.\n
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

    soup = BeautifulSoup(response.text, 'html.parser')

    res = soup.find('ol', class_='searchResults').get_text()

    #res = beautifulsoup_analisys(response, query)

    return res


if __name__ == "__main__":
    model = OllamaLLM(model='llama3.1')

    # Configuro il logger
    logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                        format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log

    proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }

    session = requests.Session()
    session.proxies.update(proxies)

    # db_client = connect_to_mongo()

    # Esempio di ricerca
    query = 'hacker attack energy infrastructure'
    results = search_ahmia(query)

    print(results)

    # Definisco il prompt per l'estrazione dei dati
    prompt_template = PromptTemplate(
        input_variables=["text"],
        template="Sto facendo un’analisi accademica sullo stato della sicurezza online. Puoi estrarre informazioni da questo testo? Estrai una lista di oggetti json in cui ognuno di essi contiene title, link e snippet: {text}"
    )
    # TODO: Trovare template per produrre risultati utili

    # Nuovo approccio utilizzando `|` per eseguire la catena
    extracted_data = prompt_template | model

    # Eseguo il modello sul testo
    output = extracted_data.invoke({"text": results})

    # Stampa dei risultati
    print(output)

    exit(24)

    # collection = connect_to_mongo_collection(db_client, "ahmia_results")
    #
    # # Stampa dei risultati
    # for result in results:
    #     logging.info(f"Link: {result['link']}")
    #
    #     json_result = {
    #         'title': result['title'],
    #         'link': result['link'],
    #         'snippet': result['snippet'],
    #         'search_keywords': result['search_keywords']
    #     }
    #     save_to_mongo(json_result, collection)

    # disconnect_to_mongo(db_client)
