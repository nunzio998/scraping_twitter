"""
Questo script ha lo scopo di trovare gli utenti correlati, per ognuno degli utenti di cui abbiamo già fatto scraping, ed estrane le informazioni.\n
Gli utenti di cui abbiamo già estratto le info si trovano nella collection 'users_info'. Per ognuno di questi si cercano i correlati
e per ogni utente correlato trovato si effettua lo scraping e si salvano i risultati a db in 'user_info'.\n

Autore: Francesco Pinsone.\n
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from src.X_scraping.chrome.beautifulsoup_analisys import find_related_user, beautifulsoup_user_analisys
from src.X_scraping.chrome.utils.utils import read_json, connect_to_mongo, disconnect_to_mongo, save_user_info_to_mongo, connect_to_mongo_collection, x_login, check_user, check_limited_user


def find_related_users():
    """
    Funzione che racchiude il funzionamento dello script per intero.\n
    Dopo aver effettuato la connesione al db e aver instaziato il driver selenium (che permette l'automazione del browser)
    lo script estrapola una lista di utenti target (di cui cercare i correlati) dalla collection 'users_info' del db.\n
    Dopo aver completato la procedura di login lo script inizia la ricerca dei correlati per ognuno dei target presenti nella lista.
    Per ogni utente se ne verifica l'effettiva esistenza e si effettua un check per verificare che non sia temporaneamente limitato
    dalla piattaforma. Dopo questi check le info possono essere estratte e salvate a db.\n
    :return: None
    """
    # Connessione al database
    client = connect_to_mongo()

    # Leggo file con credenziali
    credentials = read_json("utils/credentials.json")

    chrome_options = Options()

    # Gestore del driver per semplificare la gestione del driver Chrome
    # N.B: Scaricare chromedriver e cambiare executable_path con il path del driver scaricato
    service = Service(executable_path=credentials['driver_path'])

    # Creare un'istanza del browser Chrome con le opzioni
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 1) Estrapolo la lista dei target sui quali far partire la ricerca dalla collection 'users_info'.
    # Lista dove salvare i target
    target_list = []

    # mi connetto alla collection 'users_info'
    collection = connect_to_mongo_collection(client, 'users_info')

    for document in collection.find():
        username_tag = document.get('username_tag')
        if username_tag and (username_tag.split('@')[1] not in target_list):
            # Aggiungi alla lista se non è già presente
            target_list.append(username_tag.split('@')[1])
        else:  # Prossima iterazione
            continue

    # 2) Eseguo l'accesso a X:
    driver.get('https://www.twitter.com/login')

    # Imposto un'attesa esplicita di massimo 60 secondi
    wait_login = WebDriverWait(driver, 60)

    # Aspetto che un campo di ricerca con ID 'search-input' sia visibile
    search_input_login = wait_login.until(EC.visibility_of_element_located((By.XPATH,
                                                                            '/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input')))

    time.sleep(1)

    # Effettuo il login a X
    x_login(credentials, driver)

    # 3) Per ogni utente nella lista target cerco gli utenti correlati
    for user in target_list:
        # Cerco l'utente
        driver.get(f"https://www.X.com/{user}")

        # Verifico che l'utente esista, se non esiste passo alla prossima iterazione (utente)
        if not check_user(driver, user):
            continue
        time.sleep(1)

        # Controllo se l'account è temporanemente limitato. Se lo è sarà presente il seguente bottone per mostrare il profilo, in tal caso clicco sul bottone
        check_limited_user(driver)
        time.sleep(1)

        html_content = driver.page_source

        related_users = find_related_user(html_content)

        print(f"{user}:{related_users}")

        # 4) Ora, per ognuno degli utenti correlati trovati, cerco le informazioni utente e le salvo nel database nella collection 'users_info'
        if related_users is not None:
            for user_related in related_users:
                # Cerco l'utente
                driver.get(f"https://www.X.com/{user_related}")

                # Verifico che l'utente esista, se non esiste passo alla prossima iterazione (utente)
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
                    continue

                # Controllo se l'utente è già presente nel database
                doc = collection.find_one({'username_tag': res['username_tag']})
                if doc:
                    print('Utente già presente:', res['username_tag'])
                    continue

                # Salvo le informazioni nel database
                save_user_info_to_mongo(res, collection)
                print(f"info utente {user_related} salvate nel database..")

    driver.quit()
    disconnect_to_mongo(client)


if __name__ == "__main__":
    find_related_users()
