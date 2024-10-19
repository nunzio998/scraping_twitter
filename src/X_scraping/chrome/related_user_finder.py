import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

from beautifulsoup_analisys import find_related_user, beautifulsoup_user_analisys
from utils.utils import read_json, connect_to_mongo, disconnect_to_mongo, save_user_info_to_mongo, \
    connect_to_mongo_collection, x_login

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
search_input_login = wait_login.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input')))

time.sleep(1)

# Effettuo il login a X
x_login(credentials, driver)

# 3) Per ogni utente nella lista target cerco gli utenti correlati
for user in target_list:
    # Cerco l'utente
    driver.get(f"https://www.X.com/{user}")

    # Verifico che l'utente esista, se non esiste passo alla prossima iterazione
    try:
        # Attendo caricamento pagina
        wait_user = WebDriverWait(driver, 120)

        # Aspettare che un elemento indicativo del completo caricamento della pagina sia visibile
        search_tweets = wait_user.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[1]/div[1]/div/div/div/div/div/div[2]/div/h2')))
    except TimeoutException:
        print(f"TimeoutException: utente {user} non trovato..")
        continue

    time.sleep(1)

    # Controllo se l'account è temporanemente limitato. Se lo è sarà presente il seguente bottone per mostrare il profilo, in tal caso clicco sul bottone
    try:
        show_profile_button = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div[2]/div/button')
        show_profile_button.send_keys(Keys.RETURN)
    except NoSuchElementException:
        print("Account non limitato..")
        pass

    time.sleep(1)

    html_content = driver.page_source

    related_users = find_related_user(html_content)

    print(f"{user}:{related_users}")

    # 4) Ora, per ognuno degli utenti correlati trovati, cerco le informazioni utente e le salvo nel database nella collection 'users_info'
    if related_users is not None:
        for user_related in related_users:
            # Cerco l'utente
            driver.get(f"https://www.X.com/{user_related}")

            # Verifico che l'utente esista, se non esiste passo alla prossima iterazione
            try:
                # Attendo caricamento pagina
                wait_user = WebDriverWait(driver, 120)

                # Aspettare che un elemento indicativo del completo caricamento della pagina sia visibile
                search_tweets = wait_user.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[1]/div[1]/div/div/div/div/div/div[2]/div/h2')))
            except TimeoutException:
                print(f"TimeoutException: utente {user_related} non trovato..")
                continue

            time.sleep(1)

            # Controllo se l'account è temporanemente limitato. Se lo è sarà presente il seguente bottone per mostrare il profilo, in tal caso clicco sul bottone
            try:
                show_profile_button = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div[2]/div/button')
                show_profile_button.send_keys(Keys.RETURN)
            except NoSuchElementException:
                print("Account non limitato..")
                pass

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
