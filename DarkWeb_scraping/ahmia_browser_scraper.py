import requests
from bs4 import BeautifulSoup
from utils import connect_to_mongo, connect_to_mongo_collection, save_to_mongo, disconnect_to_mongo

proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

session = requests.Session()
session.proxies.update(proxies)

client = connect_to_mongo()


# Funzione per cercare in Ahmia
def search_ahmia(query):
    """
    Funzione per cercare in Ahmia, uno dei motori di ricerca per il dark web.
    :param query:
    :return:
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

    soup = soup.body

    results = []
    for result in soup.find_all('li', class_='result'):  # scorre la lista degli elementi che risultano dalla ricerca.
        title = result.find('a').text
        link = result.find('a')['href']
        snippet = result.find('p').text
        search_keywords = query.split(' ')
        results.append({'title': title, 'link': link, 'snippet': snippet, 'search_keywords': search_keywords})

    return results


# Esempio di ricerca
query = 'hacker attack energy infrastructure'
results = search_ahmia(query)

collection = connect_to_mongo_collection(client, "ahmia_results")

# Stampa dei risultati
for result in results:
    # print(f"Title: {result['title']}")
    print(f"Link: {result['link']}")
    # print(f"Snippet: {result['snippet']}\n")
    # print(f"Keywords: {result['search_keywords']}\n")
    json_result = {
        'title': result['title'],
        'link': result['link'],
        'snippet': result['snippet'],
        'search_keywords': result['search_keywords']
    }
    save_to_mongo(json_result, collection)

disconnect_to_mongo(client)
