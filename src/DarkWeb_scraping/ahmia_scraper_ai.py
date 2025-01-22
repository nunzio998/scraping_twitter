"""
Questo script è progettato per eseguire scraping del motore di ricerca Ahmia, uno dei principali motori di ricerca nel
dark web, e integra l'analisi dei risultati tramite un modello di linguaggio avanzato, Ollama. L'obiettivo principale è
estrarre e strutturare informazioni rilevanti dai risultati della ricerca di Ahmia, utilizzando il modello Ollama per
l'elaborazione semantica dei contenuti.

Lo script funziona configurando il proxy Tor per navigare in modo anonimo attraverso la rete Tor, assicurando che le
richieste HTTP siano anonimizzate. Successivamente, viene inviata una query al motore di ricerca Ahmia (versione onion)
e i risultati vengono estratti dal contenuto HTML, focalizzandosi sul tag `<ol>` che contiene l'elenco dei risultati.
Una volta ottenuti i dati grezzi, questi vengono inviati al modello Ollama per un'elaborazione semantica, con
l'obiettivo di estrarre informazioni strutturate come il titolo, il link e uno snippet per ogni risultato.

Al momento, i risultati elaborati vengono stampati nel terminale, ma non vengono ancora salvati nel database. Questa
parte dello script è in fase di sviluppo, poiché il sistema è ancora in fase di ottimizzazione per perfezionare il
prompt e migliorare la consistenza dei risultati restituiti dal modello Ollama. Il futuro obiettivo è garantire che il
modello fornisca risultati consistenti e formattati in modo stabile, con la possibilità di archiviare i dati in un
database.

Il motore di ricerca Ahmia è accessibile attraverso l'indirizzo onion, utilizzando la rete Tor per garantire
l'anonimato. I risultati vengono estratti con l'ausilio di BeautifulSoup, una libreria Python per il parsing di HTML.
Il modello Ollama è utilizzato per generare risposte strutturate e analizzare i contenuti ottenuti dal motore di
ricerca. L'integrazione tra il modello LLM e il codice di scraping avviene tramite langchain_ollama.

**Autore**: Francesco Pinsone
"""
import requests
import logging
from bs4 import BeautifulSoup
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate


# Funzione per cercare in Ahmia
def search_ahmia(session, query):
    """
    Funzione per eseguire una ricerca nel motore di ricerca Ahmia (dark web) utilizzando una query specificata.
    La funzione invia la query ad Ahmia e, una volta ricevuta la risposta, estrae e restituisce il testo dei risultati
    dalla pagina web, focalizzandosi sul contenuto del tag 'ol' che contiene l'elenco dei risultati della ricerca.

    **Passaggi principali**:\n
    1. **Costruzione dell'URL**: La query di ricerca viene utilizzata per costruire l'URL del motore di ricerca Ahmia, utilizzando la versione onion (buona per la navigazione anonima tramite Tor).\n
    2. **Invio della richiesta**: La funzione invia la richiesta HTTP tramite una sessione configurata con Tor per proteggere l'anonimato.\n
    3. **Gestione degli errori**: Se si verifica un errore nella connessione o nella risposta, viene restituito un messaggio di errore e una lista vuota.\n
    4. **Analisi del contenuto HTML**: La risposta viene analizzata con BeautifulSoup per estrarre il contenuto del tag `<ol>` che contiene l'elenco dei risultati della ricerca.\n
    5. **Restituzione dei risultati**: Il testo estratto dal tag 'ol' viene restituito come risultato della funzione.\n

    **Nota**: La funzione assume che i risultati di ricerca siano contenuti all'interno di un tag `<ol>` con una classe chiamata `searchResults`.\n

    :param query: stringa, la query di ricerca da inviare a Ahmia.\n
    :return: stringa, il testo estratto dal tag `<ol>` contenente i risultati della ricerca.
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

    # res = beautifulsoup_analisys(response, query)

    return res


def darkweb_ollama_scraper():
    """
    Funzione di scraping per il dark web, che integra la ricerca sul motore Ahmia con l'elaborazione dei risultati tramite il modello Ollama.
    Inizialmente, la funzione effettua la configurazione del proxy Tor, esegue la ricerca sul dark web, e successivamente invia i risultati
    a Ollama per l'elaborazione e l'estrazione di informazioni strutturate. I risultati non sono ancora salvati nel database, poiché il sistema
    è in fase di sviluppo per perfezionare il prompt e i risultati restituiti dal modello.

    **Passaggi principali**:\n
    1. **Impostazione del Proxy Tor**: Si configurano i proxy per navigare in modo anonimo attraverso Tor.\n
    2. **Ricerca su Ahmia**: La funzione `search_ahmia()` invia una query al motore di ricerca del dark web Ahmia e raccoglie i risultati.\n
    3. **Elaborazione con Ollama**: I risultati vengono inviati al modello Ollama per estrarre informazioni specifiche come il titolo, il link e lo snippet.\n
    4. **Stampa dei Risultati**: I risultati elaborati vengono stampati, ma non sono ancora salvati nel database in quanto il sistema è in fase di ottimizzazione.\n
    5. **Sviluppi futuri**: L'obiettivo è migliorare la consistenza dei risultati e perfezionare il prompt per garantire formati stabili di output.\n

    :return: Nessun valore restituito, stampa solo i risultati elaborati.
    """
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
    results = search_ahmia(session, query)

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


if __name__ == "__main__":
    darkweb_ollama_scraper()
