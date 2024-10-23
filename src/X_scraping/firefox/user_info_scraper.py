"""
Script che ha la funzione di estrarre le informazioni principali di uno o più utenti X.\n
Gli utenti da sottoporre a questo processo vengono estratti dalle varie collection, ovvero dai dati
relativi ai tweet raccolti fino a quel momento. Si considerano quindi tutti gli autori dei tweet salvati.\n

Autore: Francesco Pinsone.
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from src.X_scraping.firefox.beautifulsoup_analisys import beautifulsoup_user_analisys
from src.X_scraping.firefox.utils.utils import read_json, connect_to_mongo, disconnect_to_mongo, save_user_info_to_mongo, \
    connect_to_mongo_collection, get_db, x_login, check_user, check_limited_user


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

    # Geckodriver
    service = Service('driver/geckodriver')

    # Inizializzo driver  Firefox
    driver = webdriver.Firefox(service=service)
    # driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

    # Loggarsi manualmente su Twitter
    driver.get('https://www.twitter.com/login')

    # Imposto un'attesa esplicita di massimo 60 secondi
    wait_login = WebDriverWait(driver, 60)

    # Aspetto che un campo di ricerca con ID 'search-input' sia visibile
    search_input_login = wait_login.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input')))

    time.sleep(1)

    # Effettuo il login a X
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

        # Verifico che l'utente esista, se non esiste passo alla prossima iterazione
        if not check_user(driver, user):
            continue
        time.sleep(1)

        # Controllo se l'account è temporanemente limitato. Se lo è sarà presente il seguente bottone per mostrare il profilo, in tal caso clicco sul bottone
        check_limited_user(driver)
        time.sleep(1)

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
