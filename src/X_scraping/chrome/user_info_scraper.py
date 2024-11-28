"""
Script che ha la funzione di estrarre le informazioni principali di uno o più utenti X.\n
Gli utenti da sottoporre a questo processo vengono estratti dalle varie collection, ovvero dai dati
relativi ai tweet raccolti fino a quel momento. Si considerano quindi tutti gli autori dei tweet salvati.\n

Autore: Francesco Pinsone.
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
    Funzione che racchiude l'intero funzionamento dello script.\n
    Dopo aver effettuato la connessione al db estrae una lista di utenti target da tutte le collection che contengono
    dati relativi ai tweet salvati. Effettua poi la procedura di login ad X e in seguito inizia lo scraping delle info
    per ognuno degli utenti presenti nella lista dei target. Ad ogni iterazione le informazioni raccolte vengono salvate
    a db nella collection 'users_info'.\n
    :return None:
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
