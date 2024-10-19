import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from beautifulsoup_analisys import beautifulsoup_user_analisys
from utils.utils import read_json, connect_to_mongo, disconnect_to_mongo, save_user_info_to_mongo, \
    connect_to_mongo_collection, get_db, x_login

# Connessione al database
client = connect_to_mongo()

db = get_db(client)


# Creo una lista vuota per i target
target_list = []
# Prendo tutti i target dai documenti presenti in tutte le collezioni del db
for collection_name in db.list_collection_names():
    if collection_name != 'users_info'and collection_name != 'target_groups':
        collection = connect_to_mongo_collection(client, collection_name)
        for document in collection.find():
            username_tag = document.get('username_tag')
            if username_tag and (username_tag.split('@')[1] not in target_list):
                # Aggiungi alla lista se non è già presente
                target_list.append(username_tag.split('@')[1])
            else: # Prossima iterazione
                continue
    else: # Prossima iterazione
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
    # Cerco l'utente
    driver.get(f"https://www.X.com/{user}")

    # Verifico che l'utente esista, se non esiste passo alla prssima iterazione
    try:
        # Attendo caricamento pagina
        wait_user = WebDriverWait(driver, 120)

        # Aspettare che un elemento indicativo del completo caricamento della pagina sia visibile
        search_tweets = wait_user.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[1]/div[1]/div/div/div/div/div/div[2]/div/h2')))
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

    # Controllo se l'utente è già presente nel database
    doc = collection.find_one({'username_tag': res['username_tag']})
    if doc:
        print('Utente già presente:', res['username_tag'])
        continue

    # 3) Salvo i risultati nel database
    save_user_info_to_mongo(res, collection)

    print(res)

driver.quit()
disconnect_to_mongo(client)
