"""
Questo script automatizza il processo di ricerca e raccolta delle informazioni sugli utenti correlati su X (precedentemente noto come Twitter), partendo da una lista di utenti di cui sono già state estratte informazioni.

**Funzionamento**:\n
1. **Estrazione della lista degli utenti target**: Lo script estrae gli utenti per i quali sono già presenti informazioni nella collection `users_info` del database MongoDB. Per ogni utente estratto, il suo nome utente (username) viene utilizzato per trovare utenti correlati.

2. **Automazione del browser**: Utilizzando Selenium con il driver Firefox in modalità "headless" (senza interfaccia grafica), lo script interagisce automaticamente con il sito X, visitando i profili degli utenti e raccogliendo i dati necessari.

3. **Login su X**: Lo script esegue l'accesso su X utilizzando le credenziali archiviate in un file JSON.

4. **Ricerca degli utenti correlati**: Per ogni utente nella lista estratta dal database:\n
   - Lo script visita il profilo dell'utente su X.\n
   - Verifica l'esistenza dell'utente e se non è limitato temporaneamente.\n
   - Esamina il profilo per estrarre una lista di utenti correlati (ad esempio, follower, suggeriti, o correlati dalla piattaforma).\n

5. **Estrazione e salvataggio delle informazioni**: Per ogni utente correlato trovato:\n
   - Lo script visita il profilo dell'utente correlato.\n
   - Estrae le informazioni dal profilo tramite analisi del contenuto HTML con BeautifulSoup.\n
   - Verifica che l'utente non sia già presente nel database. Se non lo è, salva le informazioni raccolte nella collection `users_info`.\n

6. **Gestione degli errori**: Lo script gestisce gli utenti non trovati o temporaneamente limitati, evitando di eseguire operazioni su profili non validi o già presenti nel database.

**Autore**: Francesco Pinsone.
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from src.X_scraping.firefox.beautifulsoup_analisys import find_related_user, beautifulsoup_user_analisys
from src.X_scraping.firefox.utils.utils import read_json, connect_to_mongo, disconnect_to_mongo, save_user_info_to_mongo, \
    connect_to_mongo_collection, x_login, check_limited_user, check_user


def find_related_users():
    """
    Questa funzione automatizza il processo di ricerca degli utenti correlati su X (precedentemente noto come Twitter) utilizzando Selenium e MongoDB.

    L'operazione viene eseguita in più fasi:

    1. **Connessione al Database**: La funzione si connette a un database MongoDB per estrarre la lista di utenti target dalla collection 'users_info'. Gli utenti target sono identificati dai loro username.

    2. **Automazione del Browser**: Viene configurato un browser Firefox in modalità "headless" (senza interfaccia grafica) tramite Selenium WebDriver. Questo browser viene utilizzato per interagire automaticamente con il sito X.

    3. **Login su X**: Dopo aver configurato il browser, lo script esegue il login su X (Twitter) utilizzando le credenziali preconfigurate.

    4. **Ricerca degli Utenti Correlati**: Per ciascun utente nella lista di target:\n
        - Lo script visita il profilo dell'utente su X.\n
        - Verifica che l'utente esista e non sia temporaneamente limitato dalla piattaforma.\n
        - Estrae e salva gli utenti correlati (ad esempio, follower o utenti suggeriti) utilizzando una funzione dedicata.\n

    5. **Estrazione e Salvataggio delle Informazioni**: Per ogni utente correlato trovato:\n
        - Lo script esamina il profilo dell'utente correlato.\n
        - Estrae i dettagli rilevanti del profilo utilizzando BeautifulSoup.\n
        - Verifica se l'utente è già presente nel database e, in caso contrario, salva le informazioni nel database MongoDB.\n

    6. **Gestione degli Errori e Continuazione**: La funzione è progettata per saltare gli utenti che non possono essere trovati o che sono limitati. Inoltre, gestisce gli utenti già presenti nel database, evitando duplicazioni.

    Al termine del processo, il driver di Selenium viene chiuso e la connessione al database viene terminata.

    :return: Nessun valore ritornato.
    """
    # Connessione al database
    client = connect_to_mongo()

    # Leggo file con credenziali
    credentials = read_json("utils/conf.json")

    # Configura opzioni del browser
    firefox_options = Options()
    firefox_options.add_argument("--headless")

    # Geckodriver
    service = Service('driver/geckodriver')

    # Inizializzo driver  Firefox
    driver = webdriver.Firefox(service=service, options=firefox_options)
    # driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

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
    search_input_login = wait_login.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input')))

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
