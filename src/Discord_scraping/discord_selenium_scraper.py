"""
Questo script esegue lo scraping della versione web di Discord utilizzando Selenium per controllare il browser
e BeautifulSoup per effettuare l'analisi e il parsing dei contenuti HTML. I dati estratti (messaggi, autore, data,
contenuto e nome del canale) vengono poi salvati in un database MongoDB per essere archiviati e successivamente analizzati.

**Funzionalità principali**:
1. **Automazione del Browser**:
    - Controllo del browser Firefox con Selenium per simulare la navigazione web.
    - Accesso alla piattaforma Discord tramite login automatizzato.

2. **Recupero dei Messaggi**:
    - Per ogni server e canale specificato, esegue lo scraping dei messaggi presenti nella cronologia visibile.
    - Permette di scorrere verso l'alto per caricare messaggi precedenti.

3. **Parsing con BeautifulSoup**:
    - Analizza il contenuto HTML scaricato per estrarre i messaggi e le relative informazioni.
    - Restituisce una struttura JSON contenente i campi `author`, `date`, `content` e `channel_name`.

4. **Salvataggio su Database MongoDB**:
    - I dati estratti vengono organizzati per server e salvati in collezioni separate nel database.

**Limiti attuali**:
    - La gestione dei CAPTCHA durante il login a Discord non è completamente automatizzata.
    - Richiede che i target (server e canali) siano specificati e configurati correttamente nel database MongoDB.

**Autore**: Francesco Pinsone.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver

from src.Discord_scraping.utils.utils import read_json, beautifulsoup_analisys, connect_to_mongo, save_to_mongo, connect_to_mongo_collection, disconnect_to_mongo, login
import logging


def discord_scraper():
    """
    Questa funzione rappresenta il cuore dello script, gestendo il flusso di lavoro necessario per eseguire lo scraping
    dei messaggi dalla versione web di Discord. Combina l'uso di Selenium per la navigazione automatizzata e BeautifulSoup
    per il parsing dei dati HTML.

    **Passaggi principali**:\n
    1. **Configurazione del Logger**:\n
        - Imposta un logger per registrare eventi e informazioni durante l'esecuzione dello script.\n

    2. **Lettura della Configurazione**:\n
        - Carica i parametri principali, come credenziali di accesso e numero di scroll da eseguire, da un file JSON.\n

    3. **Inizializzazione di Selenium**:\n
        - Avvia il browser Firefox utilizzando il driver Selenium e configura il servizio necessario.\n

    4. **Accesso a Discord Web**:\n
        - Esegue automaticamente il login a Discord utilizzando una funzione dedicata (`login`).\n

    5. **Connessione al Database**:\n
        - Si connette a un database MongoDB per accedere alla lista di server e canali da analizzare.\n

    6. **Navigazione e Scraping**:\n
       - Per ogni server e canale specificato:\n
            - Carica la pagina corrispondente su Discord Web.\n
            - Attende che la pagina sia completamente caricata.\n
            - Scorre verso l'alto per caricare messaggi aggiuntivi, se necessario.\n
            - Utilizza la funzione `beautifulsoup_analisys` per effettuare il parsing del contenuto HTML, estraendo:\n
                - Lista dei messaggi con campi `author`, `date`, `content`.\n
                - Nome del server (`server_name`).\n
                - Nome del canale (`channel_name`).\n

    7. **Salvataggio dei Dati**:\n
        - Organizza i dati estratti per server e li salva in collezioni separate nel database MongoDB.\n

    8. **Chiusura delle Risorse**:\n
        - Disconnette il database e chiude il browser controllato da Selenium.\n

    **Nota**:\n
        - La funzione è progettata per gestire un flusso di lavoro modulare e scalabile, rendendo facile l'aggiunta di nuove funzionalità.\n
        - È possibile ottimizzare ulteriormente la gestione dei CAPTCHA e migliorare la velocità di scraping.\n

    **Limiti**:\n
        - La gestione del CAPTCHA durante il login richiede intervento manuale.\n
        - La funzione presuppone che i target di scraping siano correttamente configurati nel database.\n

    :return: Nessun valore restituito.
    """
    # Configuro il logger
    logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                        format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log

    conf = read_json("utils/conf.json")

    # Inizializzo il service selenium
    service = Service('driver/geckodriver')

    # Inizializzo driver  Firefox
    driver = webdriver.Firefox(service=service)

    # Effettuo il login a Discord
    login(driver, logging, conf)

    # Mi connetto al database
    client = connect_to_mongo()

    # Ottengo la lista dei target presenti nel database
    targets_collection = connect_to_mongo_collection(client, "discord_target")
    documents = targets_collection.find()
    target_list = [(doc['server_id'], doc['channel_id']) for doc in documents]

    for server_id, channel_id in target_list:
        # carico la pagina del server su cui voglio fare scraping
        search_url = f'https://discord.com/channels/{server_id}/{channel_id}'
        driver.get(search_url)

        # Attendo caricamento pagina
        wait_messages = WebDriverWait(driver, 120)

        # Aspettare che un elemento indicativo del completo caricamento della pagina sia visibile
        search_messages = wait_messages.until(EC.visibility_of_element_located((By.CLASS_NAME, 'panels_a4d4d9')))

        # Numero di volte che vuoi scorrere verso l'alto
        scroll_times = conf["scroll_times"]

        # Lista per salvare tutti i messaggi, nome del server e nome del canale
        all_messages, server_name, channel_name = beautifulsoup_analisys(driver, scroll_times)

        # Mi connetto alla collezione relativa al server da cui voglio estrarre i dati, se non esiste la creo
        collection = connect_to_mongo_collection(client, server_name)

        for message in all_messages:
            message_to_save = {
                'author': message['author'],
                'date': message['date'],
                'content': message['content'],
                'channel_name': channel_name
            }
            save_to_mongo(message_to_save, collection)

    disconnect_to_mongo(client)
    driver.quit()


if __name__ == "__main__":
    discord_scraper()
    # TODO: gestire meglio captcha durante l'accesso a Discord web.
