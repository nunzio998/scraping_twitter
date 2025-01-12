"""
Script per l'estrazione automatica delle informazioni di profili utente da X (precedentemente noto come Twitter).

Questo script esegue il login a X, estrae gli utenti target da un database MongoDB contenente dati relativi ai tweet raccolti,
e raccoglie informazioni specifiche su ciascun utente tramite una navigazione automatica su X. Le informazioni raccolte includono
dati come nome utente, biografia, numero di follower, tweet recenti e altre metriche pertinenti.

Le informazioni estratte vengono successivamente salvate in una collection del database MongoDB, denominata `users_info`,
per una successiva analisi.

**Funzionalità principali**:\n
1. **Estrazione degli Utenti Target**: Lo script estrae gli utenti da tutte le collezioni del database MongoDB che contengono dati relativi ai tweet, ad eccezione delle collection `users_info` e `target_groups`. Gli utenti sono identificati tramite il campo `username_tag` presente in ciascun documento. La lista di utenti viene generata evitando duplicati.\n

2. **Login a X**: Utilizzando le credenziali memorizzate in un file JSON, lo script effettua il login su X. La sessione di login viene automatizzata tramite il driver Firefox di Selenium in modalità "headless" (senza interfaccia grafica).\n

3. **Raccolta delle Informazioni sui Profili**:\n
    Per ciascun utente nella lista di target, lo script:\n
   - Accede al profilo dell'utente su X.\n
   - Verifica che il profilo esista e che l'account non sia limitato.\n
   - Raccoglie le informazioni pubblicamente visibili sul profilo, tra cui nome utente, bio, numero di follower, tweet recenti e altre statistiche.\n
   - Gestisce automaticamente eventuali account limitati, come nel caso in cui l'account sia stato bloccato temporaneamente.\n

4. **Analisi HTML tramite BeautifulSoup**: Una volta che la pagina del profilo utente è stata caricata, lo script utilizza BeautifulSoup per analizzare l'HTML e estrarre le informazioni pertinenti dal contenuto.\n

5. **Salvataggio delle Informazioni nel Database**: Le informazioni estratte da ciascun profilo vengono salvate nel database MongoDB nella collection `users_info`, per l'archiviazione e l'analisi futura.\n

6. **Gestione degli Errori**: Lo script è progettato per proseguire con la raccolta dei dati anche se un utente non viene trovato, se il profilo è limitato o se si verificano altri errori. In questi casi, il processo non viene interrotto e il sistema continua con il successivo utente.\n

7. **Chiusura delle Risorse**: Alla fine del processo di scraping, il driver di Selenium viene correttamente chiuso e la connessione al database MongoDB viene terminata.\n

**Autore**: Francesco Pinsone.
"""
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from src.X_scraping.chrome.beautifulsoup_analisys import beautifulsoup_user_analisys
from src.X_scraping.chrome.utils.utils import read_json, connect_to_mongo, disconnect_to_mongo, save_user_info_to_mongo, \
    connect_to_mongo_collection, get_db, x_login


def scrape_user_info():
    """
    Funzione che automatizza la raccolta delle informazioni sui profili utente da X (precedentemente noto come Twitter).
    Lo script esegue il login su X, esegue la ricerca di utenti target estratti da tutte le collezioni di tweet nel database
    e raccoglie le informazioni associate a ciascun utente. Le informazioni estratte vengono poi salvate nel database MongoDB,
    nella collection 'users_info'. Questo processo permette di ottenere dettagli rilevanti sugli utenti coinvolti, come il loro
    nome utente, bio, numero di follower, post recenti, e altre informazioni pertinenti.

    **Funzionamento del Processo**:\n
    1. **Connessione al Database**: La funzione si connette al database MongoDB per estrarre una lista di utenti target da tutte le collezioni che contengono dati relativi ai tweet salvati (eccetto le collection `users_info` e `target_groups`). Gli utenti vengono identificati tramite il campo `username_tag`.\n

    2. **Creazione della Lista di Target**: Lo script attraversa tutte le collezioni del database, estraendo il campo `username_tag` da ciascun documento che contiene informazioni sui tweet. Gli username vengono aggiunti a una lista, evitando duplicati.\n

    3. **Preparazione per l'Automazione del Browser**: Utilizzando Selenium e il driver Firefox in modalità "headless" (senza interfaccia grafica), viene configurato il browser per simulare la navigazione su X e raccogliere informazioni sui profili utente.\n

    4. **Login su X**: Dopo aver configurato il browser, la funzione effettua il login su X utilizzando le credenziali memorizzate in un file JSON.\n

    5. **Raccolta delle Informazioni sugli Utenti**:\n
       - Per ciascun utente nella lista di target, lo script esegue una ricerca sul suo profilo su X.\n
       - Se l'utente esiste, lo script raccoglie le informazioni disponibili sul suo profilo, come il nome, la bio, i follower, i tweet recenti, e altre metriche.\n
       - Se l'utente è limitato temporaneamente (ad esempio, se il profilo è stato bloccato per qualche motivo), lo script gestisce automaticamente questa situazione e prosegue.\n

    6. **Analisi con BeautifulSoup**: Una volta che il contenuto HTML del profilo dell'utente è stato caricato, viene passato a BeautifulSoup per l'analisi e l'estrazione delle informazioni rilevanti. Questo permette di strutturare i dati in un formato utile per il salvataggio nel database.\n

    7. **Salvataggio nel Database**: Le informazioni estratte da ciascun profilo utente vengono salvate nella collection `users_info` del database MongoDB.\n

    8. **Gestione degli Errori**: Se un utente non viene trovato o se si verificano errori durante la raccolta dei dati (ad esempio, l'utente ha un profilo limitato o non è accessibile), lo script continua automaticamente con il prossimo utente, senza interrompere l'esecuzione.\n

    9. **Chiusura delle Risorse**: Al termine dell'operazione di scraping, il driver di Selenium viene chiuso correttamente e la connessione al database viene terminata.\n

    :return: Nessun valore restituito. Le informazioni sugli utenti vengono salvate direttamente nel database.
    """
    # Connessione al database
    client = connect_to_mongo()

    db = get_db(client)

    # Creo una lista vuota per i target
    target_list = []
    # Prendo tutti i target dai documenti presenti in tutte le collezioni del db
    for collection_name in db.list_collection_names():
        if collection_name != 'users_info' and collection_name != 'target_groups':
            collection = connect_to_mongo_collection(client, collection_name)
            for document in collection.find():
                username_tag = document.get('username_tag')
                if username_tag and (username_tag not in target_list):
                    # Aggiungi alla lista se non è già presente
                    target_list.append(username_tag)
                else:  # Prossima iterazione
                    continue
        else:  # Prossima iterazione
            continue

    # Leggo file con credenziali
    credentials = read_json("utils/credentials.json")

    collection = connect_to_mongo_collection(client, 'users_info')

    # 1) Eseguo l'accesso a X:

    # Configura opzioni del browser
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Avvia in modalità headless
    chrome_options.add_argument("--disable-gpu")  # Opzione per migliorare la compatibilità
    chrome_options.add_argument("--no-sandbox")  # Utile per ambienti server
    chrome_options.add_argument("--disable-dev-shm-usage")  # Migliora la gestione della memoria

    # Gestore del driver per semplificare la gestione del driver Chrome
    # service = Service(ChromeDriverManager().install()) # Decommentare per scaricare il driver all'avvio del programma
    service = Service(credentials['driver_path'])

    # Creare un'istanza del browser Chrome con le opzioni
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Loggarsi manualmente su Twitter
    driver.get('https://www.twitter.com/login')

    # Imposto un'attesa esplicita di massimo 60 secondi
    wait_login = WebDriverWait(driver, 60)

    # Aspetto che un campo di ricerca con ID 'search-input' sia visibile
    search_input_login = wait_login.until(EC.visibility_of_element_located((By.XPATH,
                                                                            '/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input')))

    time.sleep(1)

    # Effettuo il login ad X
    x_login(credentials, driver)

    # 2) Eseguo la ricerca degli utenti:
    for user in target_list:
        # Controllo se l'utente è già presente nel database
        doc = collection.find_one({'username_tag': user})
        if doc:
            print('Utente già presente:', user)
            continue

        # Cerco l'utente
        driver.get(f"https://www.X.com/{user}")

        # Verifico che l'utente esista, se non esiste passo alla prssima iterazione

        try:
            # Attendo caricamento pagina
            wait_user = WebDriverWait(driver, 120)

            # Aspettare che un elemento indicativo del completo caricamento della pagina sia visibile
            search_tweets = wait_user.until(EC.visibility_of_element_located((By.XPATH,
                                                                              '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[1]/div[1]/div/div/div/div/div/div[2]/div/h2')))
        except TimeoutException:
            print(f"TimeoutException: utente {user} non trovato..")
            continue

        time.sleep(2)

        html_content = driver.page_source

        # Analisi con BeautifulSoup
        res = beautifulsoup_user_analisys(html_content)

        if res['username_tag'] is None:
            print('Utente non trovato:', user)
            continue

        # 3) Salvo i risultati nel database
        save_user_info_to_mongo(res, collection)

        print(res)

    driver.quit()
    disconnect_to_mongo(client)


if __name__ == "__main__":
    scrape_user_info()
