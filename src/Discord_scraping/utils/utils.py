"""
Questo script fornisce una serie di funzioni utili per interagire con il sito web di Discord, eseguire scraping dei messaggi in una chat e interagire con un database MongoDB. Le funzionalità principali incluse in questo script sono:

1. **Gestione MongoDB**:\n
   - Connessione a un database MongoDB tramite una stringa di connessione.\n
   - Connessione a specifiche collezioni MongoDB, con la possibilità di crearle se non esistono.\n
   - Salvataggio dei dati nel database MongoDB.\n

2. **Analisi dei dati con BeautifulSoup**:\n
   - Estrazione e parsing dei messaggi da una pagina web tramite il modulo BeautifulSoup.\n
   - Raccolta dei messaggi da una chat di Discord, insieme ai metadati relativi all'autore, alla data e al contenuto del messaggio.\n

3. **Interazioni con Discord tramite Selenium**:\n
   - Automazione del login a Discord usando Selenium, includendo la gestione di un possibile captcha.\n
   - Navigazione tra le pagine di Discord per raccogliere messaggi da una chat.\n
   - Scroll della pagina per caricare più messaggi tramite l'interazione con la pagina HTML.\n

4. **Gestione delle sessioni con i cookies**:\n
   - Caricamento dei cookies di sessione da un file JSON per superare eventuali sistemi di autenticazione come il captcha.\n

5. **Logging**:\n
   - Logging delle operazioni eseguite per monitorare l'avanzamento e il successo o il fallimento delle azioni (ad esempio, la connessione al database, l'esecuzione dello scraping, il login a Discord, ecc.).\n

Lo script è progettato per operare in un ambiente automatizzato di scraping di chat Discord, ma include anche la gestione di eventuali ostacoli come il captcha. È inoltre integrato con MongoDB per il salvataggio dei dati raccolti.

**Prerequisiti**:\n
- Una connessione attiva a un database MongoDB.\n
- I cookies di sessione per evitare il login manuale ripetuto (se necessario).\n
- Un ambiente con Selenium e BeautifulSoup per l'automazione del browser e l'analisi del contenuto delle pagine.\n

**Uso**:\n
Lo script può essere utilizzato per raccogliere e analizzare messaggi da una chat di Discord, quindi salvare i dati nel database MongoDB per ulteriori elaborazioni. Le credenziali per il login a Discord devono essere fornite tramite un file di configurazione. Inoltre, lo script gestisce automaticamente il login e la risoluzione di eventuali captcha.

**Autore**: Francesco Pinsone.
"""

import json
import re
import time
import pymongo
from bs4 import BeautifulSoup
from selenium.common import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import logging

# Configuro il logger
logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                    format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log


def read_json(path):
    """
    Funzione per leggere il contenuto di un file JSON e restituirlo come dizionario.

    **Funzionamento**:\n
    1. **Apertura del file**: Apre il file JSON specificato dal percorso `path` in modalità lettura.\n
    2. **Caricamento del contenuto**: Utilizza la funzione `json.load` per caricare il contenuto del file JSON e convertirlo in un oggetto Python (dizionario).\n
    3. **Restituzione dei dati**: Una volta letto il file, la funzione restituisce il dizionario contenente i dati del file JSON.\n

    :param path: str, il percorso del file JSON da leggere.\n
    :return: dict, i dati contenuti nel file JSON, rappresentati come un dizionario Python.
    """
    with open(path, 'r') as file:
        return json.load(file)


config_data = read_json('/Users/francesco/Documents/Campus Biomedico/2 anno/II Semestre/Tesi/python_workspace/src/Discord_scraping/utils/conf.json')


# Funzioni MongoDB:
def connect_to_mongo():
    """
    Funzione che consente di stabilire una connessione con un database MongoDB utilizzando una stringa di connessione.

    **Passaggi principali**:\n
    1. **Connessione al Database**: Utilizza la stringa di connessione predefinita, configurata nel file di configurazione, per stabilire la connessione con il server MongoDB.\n
    2. **Verifica della Connessione**: Esegue un comando `ping` sul database per verificare se la connessione è attiva. Se la connessione ha successo, viene registrato un log con la versione del server MongoDB.\n
    3. **Gestione degli Errori**: Se si verifica un errore durante il tentativo di connessione, l'errore viene registrato nel log.\n

    **Nota**: Il client MongoDB viene creato utilizzando la libreria `pymongo`, e la connessione viene stabilita utilizzando la stringa di connessione definita nel file di configurazione.\n

    :return: client, oggetto che rappresenta la connessione attiva al database MongoDB.
    """
    connection_string = config_data['connection_string']
    client = pymongo.MongoClient(connection_string)
    # Provo a connettermi al database
    try:
        client.admin.command('ping')
        logging.info("Connesso al database: " + client.server_info()["version"])
    except Exception as e:
        logging.exception(e)

    return client


def disconnect_to_mongo(client):
    """
    Funzione che consente di disconnettersi dal database MongoDB, chiudendo la connessione attiva.

    **Passaggi principali**:\n
    1. **Log della Disconnessione**: La funzione registra un log che indica la disconnessione dal database, includendo la versione del server MongoDB al quale era connesso.\n
    2. **Chiusura della Connessione**: Una volta eseguito il log, la connessione al database viene chiusa, liberando le risorse.\n

    **Nota**: La funzione utilizza il metodo `server_info()` per recuperare informazioni sul server, come la versione, che verranno incluse nel log.\n

    :param client: Oggetto di connessione al database MongoDB. Deve essere un client MongoDB valido, creato con una libreria come `pymongo`.\n
    :return: Nessun valore restituito. La funzione esegue solo l'azione di disconnessione dal database.
    """
    logging.info("Disconnesso dal database: " + client.server_info()["version"])
    client.close()


def connect_to_mongo_collection(client, collection_name):
    """
    Funzione che consente di connettersi a una collezione specifica di MongoDB. Se la collezione non esiste, la funzione la crea automaticamente.

    **Passaggi principali**:\n
    1. **Connessione al Database**: La funzione si connette al database MongoDB utilizzando il client e il nome del database fornito nelle impostazioni.\n
    2. **Verifica e Creazione Collezione**: La funzione verifica se la collezione specificata esiste già nel database. Se non esiste, la funzione la crea.\n
    3. **Restituzione della Collezione**: Una volta verificata o creata la collezione, la funzione restituisce un oggetto che rappresenta la collezione, pronto per operazioni successive.\n

    **Nota**: La funzione assume che la configurazione del database (incluso il nome del database) sia disponibile attraverso un oggetto di configurazione (ad esempio `config_data`).\n

    :param client: Oggetto di connessione al database MongoDB. Deve essere un client MongoDB valido, creato con una libreria come `pymongo`.\n
    :param collection_name: Stringa che rappresenta il nome della collezione a cui ci si vuole connettere o che si vuole creare.\n
    :return: Oggetto che rappresenta la collezione MongoDB. La collezione sarà pronta per l'uso (lettura/scrittura).
    """
    db = client.get_database(config_data['database'])

    # Verifica se la collezione esiste già
    if collection_name not in db.list_collection_names():
        # Se la collezione non esiste, creala
        db.create_collection(collection_name)
        logging.info("Creata la collezione:" + collection_name)
    else:
        logging.info("La collezione esiste già:" + collection_name)

    return db.get_collection(collection_name)


def save_to_mongo(data, collection):
    """
    Funzione che salva i dati in una collezione di MongoDB. La funzione inserisce un singolo documento (dati) nella collezione specificata.

    **Passaggi principali**:\n
    1. **Salvataggio dei dati**: I dati vengono passati come un dizionario (`data`) e vengono inseriti nella collezione MongoDB fornita tramite il metodo `insert_one()`.\n
    2. **Logging**: Viene registrato un messaggio di log che conferma che i dati sono stati salvati nel database.\n

    **Nota**: Questa funzione salva i dati in un'unica operazione e non esegue controlli avanzati (ad esempio, verifica di duplicati o gestione di errori).\n

    :param data: dict, i dati da salvare nel database. Si suppone che siano nel formato appropriato per MongoDB (ad esempio, un dizionario Python).\n
    :param collection: Oggetto che rappresenta la collezione di MongoDB in cui i dati devono essere salvati.\n
    :return: Nessun valore restituito. La funzione esegue solo l'inserimento dei dati.
    """
    collection.insert_one(data)
    logging.info(f"Salvato nel db: {data}")


def beautifulsoup_analisys(driver, scroll_times):
    """
    Funzione che esegue l'analisi di una pagina web contenente messaggi (ad esempio, una chat) utilizzando il modulo BeautifulSoup.
    La funzione effettua un numero definito di scroll verso l'alto della pagina per caricare più messaggi, quindi estrae informazioni
    come il nome del server, il nome del canale e i dettagli dei messaggi (autore, data e contenuto).

    **Passaggi principali**:\n
    1. **Scroll verso l'alto**: La funzione esegue il numero di scroll richiesti tramite la funzione `scroll_up`, caricando progressivamente più messaggi.\n
    2. **Estrazione del contenuto HTML**: Dopo ogni scroll, la pagina viene analizzata con BeautifulSoup per estrarre il contenuto HTML della pagina.\n
    3. **Estrazione delle informazioni del server e del canale**: La funzione cerca nel codice HTML il nome del server e del canale.\n
    4. **Estrazione dei messaggi**: Per ogni messaggio presente nella pagina, vengono estratti l'autore, il timestamp e il contenuto del messaggio. I messaggi vuoti vengono ignorati.\n
    5. **Restituzione dei risultati**: La funzione restituisce una lista di dizionari contenenti le informazioni sui messaggi, insieme ai nomi del server e del canale.\n

    **Nota**: La funzione assume che i messaggi siano contenuti all'interno di specifici tag e classi CSS che vengono cercati tramite BeautifulSoup.\n

    :param driver: Oggetto `webdriver` di Selenium utilizzato per interagire con il browser e estrarre il contenuto HTML della pagina.\n
    :param scroll_times: Numero di volte che la funzione deve eseguire lo scroll verso l'alto per caricare più messaggi.\n
    :return:
        - list: Una lista di dizionari contenente i dettagli dei messaggi (autore, data, contenuto).\n
        - str: Nome del server trovato nella pagina.\n
        - str: Nome del canale trovato nella pagina.
    """
    all_messages = []
    server_name = None
    channel_name = None

    # Scorri verso l'alto per caricare più messaggi e salva i nuovi messaggi
    for _ in range(scroll_times):
        scroll_up(driver, 1)

        # Estraggo HTML pagina con BeautifulSoup
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        soup = soup.body

        # Trova nome server e nome canale
        server_name = soup.find('h2', class_='defaultColor_a595eb lineClamp1_a595eb text-md/semibold_dc00ef defaultColor_e42ec6 name_fd6364').text
        channel_name = soup.find('h1', class_='defaultColor_a595eb heading-md/semibold_dc00ef defaultColor_e42ec6 title_fc4f04').text.split(": ")[1]

        # Trova tutti i messaggi
        messages = soup.find_all('div', class_='contents_f9f2ca')

        for message in messages:
            # Trovo autore e data. Se non trovo l'autore vuol dire che l'autore è lo stesso del messaggio precedente quindi resta invariato
            if message.find('span', class_='username_f9f2ca desaturateUserColors_c7819f clickable_f9f2ca'):
                author = message.find('span', class_='username_f9f2ca desaturateUserColors_c7819f clickable_f9f2ca').text

            timestamp = message.find('time')['datetime']

            # Trovo il contenuto del messaggio
            content = message.find('div', class_='markup_f8f345 messageContent_f9f2ca').text
            # Se la stringa è vuota, salta il messaggio (non lo salva)
            if re.fullmatch(r'\n*', content):
                continue
            all_messages.append({'author': author, 'date': timestamp, 'content': content})

    return all_messages, server_name, channel_name


# Funzione per scorrere verso l'alto e caricare più messaggi
def scroll_up(driver, times):
    """
    Funzione che simula lo scroll verso l'alto della pagina, permettendo di caricare più messaggi o contenuti all'interno di una chat
    o una pagina dinamica. Utilizza il tasto di "Page Up" per spostarsi verso l'alto e consente di caricare progressivamente i messaggi
    o gli elementi aggiuntivi presenti nella pagina.

    **Passaggi principali**:\n
    1. **Simulazione dello scroll**: La funzione trova l'elemento principale della pagina (con il tag `<html>`) e invia il comando `Page Up` per simulare lo scroll verso l'alto.\n
    2. **Caricamento dei messaggi**: Ogni volta che viene effettuato uno scroll, la pagina potrebbe caricare ulteriori messaggi o contenuti.\n
    3. **Attesa tra gli scroll**: Dopo ogni esecuzione dello scroll, la funzione attende 2 secondi per permettere ai messaggi di caricarsi correttamente prima di effettuare un altro scroll.\n

    **Nota**: Il parametro `times` controlla il numero di volte che viene effettuato lo scroll verso l'alto. Questo è utile quando si vogliono caricare più messaggi in una chat o elementi in una pagina che utilizza il caricamento dinamico.\n

    :param driver: Oggetto `webdriver` di Selenium utilizzato per interagire con il browser e inviare i comandi di scroll.\n
    :param times: Numero di volte che la funzione deve eseguire lo scroll verso l'alto per caricare più contenuti. \n
    :return: Nessun valore restituito, la funzione agisce direttamente sul driver Selenium per eseguire lo scroll.
    """
    for _ in range(times):
        page = driver.find_element(By.TAG_NAME, 'html')
        page.send_keys(Keys.PAGE_UP)
        time.sleep(2)  # Aspetta che i messaggi vengano caricati


def load_cookies(driver, cookies_path="utils/cookies.json"):
    """
    Funzione che carica i cookies salvati da un file JSON e li aggiunge alla sessione del driver Selenium. Questo consente di riutilizzare
    una sessione precedentemente autenticata per evitare di dover ripetere il processo di login o bypassare un captcha.

    **Passaggi principali**:\n
    1. **Caricamento dei cookies**: La funzione legge il file JSON specificato nel parametro `cookies_path` e carica i cookies salvati in un oggetto Python.\n
    2. **Aggiunta dei cookies alla sessione**: I cookies caricati vengono aggiunti alla sessione del driver Selenium, permettendo al browser di simulare un accesso precedentemente effettuato.\n
    3. **Riutilizzo della sessione**: L'aggiunta dei cookies permette di mantenere la sessione attiva e di bypassare la necessità di effettuare nuovamente il login o risolvere il captcha, se i cookies contengono informazioni valide.\n

    **Nota**: Assicurarsi che il file JSON contenente i cookies sia correttamente formattato e che i cookies siano validi per la sessione corrente.\n

    :param driver: Oggetto `webdriver` di Selenium utilizzato per interagire con il browser e caricare i cookies nella sessione.\n
    :param cookies_path: Il percorso del file JSON che contiene i cookies di sessione da caricare. Il percorso predefinito è `"utils/cookies.json"`.\n
    :return: Nessun valore restituito, la funzione modifica direttamente la sessione del driver Selenium aggiungendo i cookies.
    """
    with open(cookies_path, "r") as file:
        cookies = json.load(file)
    for cookie in cookies:
        driver.add_cookie(cookie)


def login(driver, logging, credentials):
    """
    Funzione che avvia la procedura di login a Discord e successivamente verifica la presenza di un captcha. Se viene rilevato un captcha,
    la funzione si occupa di gestirlo tramite un controllo e un eventuale bypass. La funzione coordina l'esecuzione delle funzioni
    `discord_login` e `check_captcha` per garantire il corretto accesso all'account.

    **Passaggi principali**:\n
    1. **Avvio del login**: La funzione richiama `discord_login` per avviare la procedura di accesso automatizzato a Discord, utilizzando le credenziali fornite nel parametro `credentials`.\n
    2. **Verifica del captcha**: Dopo il login, la funzione chiama `check_captcha` per controllare se un captcha è presente. Se rilevato, gestisce la situazione permettendo all'utente di risolverlo manualmente.\n
    3. **Gestione dell'accesso**: La funzione garantisce che il login venga completato correttamente prima di eseguire il controllo del captcha. Se il captcha è ancora presente, la funzione invita l'utente a risolverlo.\n

    **Nota**: Il login e la verifica del captcha vengono effettuati in due fasi distinte, una per l'autenticazione e una per la gestione del captcha, assicurando che entrambi gli aspetti siano gestiti correttamente.\n

    :param driver: Oggetto `webdriver` di Selenium utilizzato per interagire con il browser, caricare la pagina di login e inviare i dati.\n
    :param logging: Oggetto di logging per registrare i dettagli del processo di login e diagnosticare eventuali problemi.\n
    :param credentials: Dizionario contenente le credenziali dell'utente (email e password) necessarie per il login su Discord.\n
    :return: Nessun valore restituito, la funzione si occupa di eseguire l'intero processo di login, inclusa la gestione del captcha.
    """
    # Effettuo il login a Discord
    discord_login(driver, logging, credentials)

    time.sleep(1)

    # Cerco la presenza di captcha, se ci sono provo a bypassarli.
    check_captcha(driver, logging, credentials)


def discord_login(driver, logging, credentials):
    """
    Funzione che automatizza la procedura di login a Discord utilizzando Selenium. La funzione carica la pagina di login di Discord,
    inserisce automaticamente le credenziali fornite e gestisce eventuali schermate o problemi durante il processo di autenticazione.

    **Passaggi principali**:\n
    1. **Caricamento della pagina di login**: La funzione apre la pagina di login di Discord utilizzando l'oggetto `driver` di Selenium.\n
    2. **Gestione della selezione dell'utente**: Se la schermata di selezione dell'utente appare, la funzione simula la pressione del pulsante "Accedi" per procedere.\n
    3. **Inserimento delle credenziali**: La funzione cerca i campi per l'email e la password sulla pagina e inserisce automaticamente i valori forniti nel parametro `credentials`.\n
    4. **Gestione degli errori**: Se uno dei campi non viene trovato, la funzione tenta di cercare l'elemento in un secondo tentativo. Se il campo è ancora assente, viene loggata l'errore e il programma si interrompe.\n
    5. **Sicurezza**: Dopo l'inserimento delle credenziali, la funzione simula la pressione del tasto "Invio" per inviare i dati di accesso e completare il login.\n
    6. **Uscita in caso di errore**: Se i campi non vengono trovati dopo i tentativi, la funzione esegue un'uscita sicura del programma per evitare l'accesso non riuscito.\n

    **Nota**: L'accesso viene effettuato utilizzando i valori passati nel parametro `credentials`, che contiene l'email e la password dell'utente.\n

    :param driver: Oggetto `webdriver` di Selenium utilizzato per interagire con il browser, caricare la pagina di login e inviare i dati.\n
    :param logging: Oggetto di logging per registrare i dettagli del processo di login e diagnosticare eventuali problemi.\n
    :param credentials: Dizionario contenente le credenziali dell'utente (email e password) necessarie per il login su Discord.\n
    :return: Nessun valore restituito, la funzione si occupa di effettuare il login automaticamente.
    """
    # Caricamento pagina di login discord
    driver.get('https://discord.com/login')

    # Imposto un'attesa esplicita di massimo 60 secondi
    wait_login = WebDriverWait(driver, 60)

    search_input_login = wait_login.until(EC.visibility_of_element_located((By.ID, 'uid_7')))

    # Controllo la presenza o meno della schermata che specifica la volontà di accedere a Discord col proprio utente o sceglierne un altro.
    # La schermata compare solitamente dopo un elevato numero di esecuzioni. Se è presente simulo la pressione del bottone "Accedi".
    try:
        access_button_field = driver.find_element(By.XPATH,
                                                  "/html/body/div[1]/div[2]/div[1]/div[1]/div/div/div/section/div[2]/div[2]/div/div/div[3]/button[1]")
        access_button_field.send_keys(Keys.RETURN)
        time.sleep(2)
    except NoSuchElementException:
        logging.info("Schermata di selezione utente assente..")

    # Cerco i campi nei quali far inserire automaticamente le credenziali
    try:
        email_field = driver.find_element(By.ID, 'uid_7')
        email_field.send_keys(credentials["email"])
        time.sleep(2)
    except NoSuchElementException:
        logging.info("Tentativo 1: Campo email non trovato..")
        try:
            email_field = driver.find_element(By.ID, 'uid_8')
            email_field.send_keys(credentials["email"])
            time.sleep(2)
        except NoSuchElementException:
            logging.info("Tentativo 2: Campo email non trovato, Impossibile effettuare l'accesso a Discord..")
            driver.quit()
            exit(-1)

    try:
        password_field = driver.find_element(By.ID, 'uid_9')
        password_field.send_keys(credentials["password"])
        password_field.send_keys(Keys.RETURN)
        time.sleep(2)
    except NoSuchElementException:
        logging.info("Tentativo 1: Campo password non trovato..")
        try:
            password_field = driver.find_element(By.ID, 'uid_10')
            password_field.send_keys(credentials["password"])
            password_field.send_keys(Keys.RETURN)
            time.sleep(2)
        except NoSuchElementException:
            logging.info("Tentativo 2: Campo password non trovato, Impossibile effettuare l'accesso a Discord..")
            driver.quit()
            exit(-1)


def check_captcha(driver, logging, credentials):
    """
    Funzione che verifica la presenza di un CAPTCHA durante il processo di login su Discord. La funzione esegue un controllo
    sulla pagina per determinare se un CAPTCHA è presente, e in caso positivo, consente all'utente di risolverlo manualmente
    prima di procedere con il login.

    **Passaggi principali**:\n
    1. **Ricerca del CAPTCHA**: La funzione cerca la presenza di un iframe che contiene il CAPTCHA nella pagina di login.\n
    2. **Gestione del CAPTCHA**: Se viene rilevato un CAPTCHA, l'utente è invitato a risolverlo manualmente. La funzione si sospende
       e attende che l'utente prema `ENTER` dopo aver completato il test.\n
    3. **Completamento della procedura di login**: Una volta che il CAPTCHA è risolto, la funzione riprende l'esecuzione e tenta di
       completare la procedura di login con le credenziali fornite.\n
    4. **Gestione degli errori**: Se il CAPTCHA non è presente, la funzione logga un messaggio e termina la procedura di login.\n
    5. **Sviluppi futuri**: In futuro, la funzione includerà la possibilità di caricare i cookies da una sessione valida tramite
       lo script `extract_cookies.py` per bypassare il CAPTCHA automaticamente, evitando l'intervento manuale.\n

    **Nota**: Attualmente la funzione prevede l'intervento manuale dell'utente per risolvere il CAPTCHA. Nei futuri sviluppi,
    la gestione automatica del CAPTCHA tramite cookies sarà implementata per semplificare il processo.

    :param driver: Oggetto `webdriver` di Selenium utilizzato per interagire con il browser e caricare la pagina di login.\n
    :param logging: Oggetto per il logging delle informazioni durante l'esecuzione dello script, utile per tracciare l'andamento del processo.\n
    :param credentials: Dizionario contenente le credenziali dell'utente per il login su Discord.\n
    :return: Nessun valore restituito.
    """
    # # Cerco la presenza del captcha, se presente cerco di bypassarlo.
    # try:
    #     captcha = driver.find_element(By.XPATH,
    #                                   "/html/body/div[2]/div[2]/div[1]/div[5]/div[2]/div/div/div/div[1]/div[4]/div/iframe")
    #     logging.info("Captcha presente, carico cookies..")
    #
    #     # Carico i cookies e faccio il refresh del driver
    #     load_cookies(driver)
    #     driver.refresh()
    #
    #     # Comando con cui si cerca di rimuovere il test captcha dal DOM.
    #     driver.execute_script("document.getElementById('captcha').style.display = 'none';")
    #
    #     # Ripeto la procedura di login
    #     discord_login(driver, logging, credentials)
    #     time.sleep(1)
    # except NoSuchElementException:
    #     logging.info("Captcha non presente..")
    #
    # # Se il captcha è ancora presente vuol dire che non sono riuscito a bypassarlo, quindi lo faccio risolvere all'utente.
    # try:
    #     captcha = driver.find_element(By.XPATH,
    #                                   "/html/body/div[2]/div[2]/div[1]/div[5]/div[2]/div/div/div/div[1]/div[4]/div/iframe")
    #     logging.info("Captcha ancora presente, risolvere manualmente..")
    #
    #     input("Premi ENTER dopo aver risolto il captcha..")
    #
    #     discord_login(driver, logging, credentials)
    #     time.sleep(1)
    # except NoSuchElementException:
    #     logging.info("Captcha non presente, procedura di login terminata..")

    try:
        captcha = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[1]/div[5]/div[2]/div/div/div/div[1]/div[4]/div/iframe")
        logging.info("Captcha presente, risolvere manualmente e premere invio dopo la risoluzione..")

        input("Premi ENTER dopo aver risolto il captcha..")
        time.sleep(1)
    except NoSuchElementException:
        logging.info("Captcha non presente, procedura di login terminata..")