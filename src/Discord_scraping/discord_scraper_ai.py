"""
Questo script è progettato per eseguire lo scraping della versione web di Discord utilizzando la libreria Selenium per il controllo del browser.
Inoltre, sfrutta un modello di linguaggio naturale avanzato (LLM, come Ollama) per effettuare il parsing e l'estrazione dei dati dai contenuti HTML
dei canali Discord in modo automatizzato e flessibile.

**Funzionalità principali**:\n
1. **Automazione del Browser**:\n
    - Effettua l'accesso alla versione web di Discord simulando un utente reale.\n
    - Naviga automaticamente attraverso i server e i canali specificati.\n

2. **Recupero dei Messaggi**:
Scarica i messaggi visibili in un canale e permette di estendere lo scraping scorrendo verso l'alto per recuperare ulteriori contenuti.\n

3. **Parsing Avanzato con LLM**:\n
    - Utilizza un modello LLM per analizzare i messaggi scaricati e convertirli in un formato strutturato (JSON).\n
    - Riconosce campi come autore, data, contenuto e nome del canale.\n

4. **Archiviazione su Database**: Al momento, i risultati elaborati vengono visualizzati nel terminale tramite log, ma non vengono ancora salvati nel database. Questa parte dello script è in fase di sviluppo, poiché il sistema è ancora in fase di ottimizzazione per perfezionare il prompt e migliorare la consistenza dei risultati restituiti dal modello Ollama. Il futuro obiettivo è garantire che il modello fornisca risultati consistenti e formattati in modo stabile, con la possibilità di archiviare i dati in un database.\\

**Limiti attuali**:\n
    - Il parsing dei messaggi tramite LLM è in fase di sviluppo e richiede un modello più performante per risultati ottimali.\n
    - La gestione del CAPTCHA durante l'accesso a Discord web è manuale e non completamente automatizzata.\n

**Autore**: Francesco Pinsone.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from src.Discord_scraping.utils.utils import read_json, connect_to_mongo, connect_to_mongo_collection, \
    disconnect_to_mongo, scroll_up, login
import logging
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from bs4 import BeautifulSoup


def discord_chatgpt_scraper() -> None:
    # TODO: Da sviluppare quando si avrà accesso all'API di Chatgpt.
    pass


def discord_ollama_scraper() -> None:
    """
    Questa funzione gestisce il flusso principale dello script, eseguendo lo scraping dei messaggi dai canali Discord specificati
    e analizzandoli tramite un modello LLM (ad es. Ollama) per estrarre informazioni strutturate.

    **Passaggi principali**:\n
    1. **Inizializzazione del modello LLM**:\n
        - Configura un modello di linguaggio naturale per effettuare il parsing avanzato dei messaggi.\n

    2. **Configurazione del logger**:\n
        - Imposta il logger per monitorare gli eventi e registrare informazioni durante l'esecuzione.\n

    3. **Lettura della configurazione**:\n
        - Carica i parametri principali, come il numero di scroll verso l'alto e credenziali di accesso, da un file JSON.\n

    4. **Inizializzazione del browser**:\n
        - Utilizza Selenium per avviare il browser Firefox e gestire l'accesso automatizzato.\n

    5. **Login su Discord Web**:\n
        - Esegue l'accesso alla piattaforma utilizzando le credenziali fornite.\n

    6. **Recupero dei target dal database**:\n
        - Si collega a un database MongoDB e recupera l'elenco dei server e canali su cui eseguire lo scraping.\n

    7. **Navigazione e scraping**:\n
        - Per ogni server e canale specificato:\n
            - Carica la pagina web corrispondente.\n
            - Attende il caricamento completo dei messaggi.\n
            - Scorre verso l'alto per caricare messaggi aggiuntivi, se richiesto.\n

    8. **Parsing dei messaggi**:\n
        - Utilizza un LLM per analizzare il contenuto HTML recuperato, estraendo i messaggi in formato JSON con i campi:\n
            - `author`: Nome dell'autore del messaggio.\n
            - `date`: Data di pubblicazione del messaggio.\n
            - `content`: Contenuto testuale del messaggio.\n
            - `channel_name`: Nome del canale di appartenenza.\n

    9. **Stampa dei Risultati**:\n
        - I risultati elaborati vengono stampati, ma non sono ancora salvati nel database in quanto il sistema è in fase di ottimizzazione.\n

    10. **Chiusura delle risorse**:\n
        - Chiude la connessione al database e termina il driver Selenium.\n

    **Nota**:\n
        - La funzione è progettata per essere espandibile, permettendo di integrare facilmente nuovi modelli LLM o strategie di scraping.\n
        - La gestione del CAPTCHA e altre interruzioni impreviste richiede ulteriori miglioramenti.\n

    **Limiti**:\n
        - Il parsing dei dati dipende dalla capacità del modello LLM utilizzato.\n
        - La gestione del caricamento dei messaggi potrebbe variare in base alla struttura HTML di Discord Web.\n

    :return: Nessun valore restituito.
    """
    model = OllamaLLM(model='llama3.1')

    # Configuro il logger
    logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                        format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log

    conf = read_json("utils/conf.json")

    # Inizializzo il service selenium
    service = Service('driver/geckodriver')

    # Inizializzo driver  Firefox
    driver = webdriver.Firefox(service=service)

    # Procedura di login
    login(driver, logging, conf)

    # Mi connetto al database
    client = connect_to_mongo()

    # Ottengo la lista dei target presenti nel database
    targets_collection = connect_to_mongo_collection(client, "discord_target")
    documents = targets_collection.find()
    target_list = [(doc['server_id'], doc['channel_id']) for doc in documents]

    prompt_template = PromptTemplate(
        input_variables=["text"],
        template="{text}. Da questo testo estrai una lista di messaggi in formato json. Ogni messaggio è composto dai campi: author, date, content e channel_name (che lascerai vuoto). Non scrivere in output nulla oltre la lista di oggetti json."
    )
    # TODO: Trovare il giusto prompt per l'estrazione dei dati

    for server_id, channel_id in target_list:
        # carico la pagina del server su cui voglio fare scraping
        search_url = f'https://discord.com/channels/{server_id}/{channel_id}'
        driver.get(search_url)

        # Attendo caricamento pagina
        wait_messages = WebDriverWait(driver, 60)

        # Aspettare che un elemento indicativo del completo caricamento della pagina sia visibile
        search_messages = wait_messages.until(EC.visibility_of_element_located((By.CLASS_NAME, 'panels_a4d4d9')))

        # Numero di volte che vuoi scorrere verso l'alto
        scroll_times = conf['scroll_times']

        scroll_up(driver, scroll_times)

        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        soup = soup.body

        server_name = soup.find('h2',
                                class_='defaultColor_a595eb lineClamp1_a595eb text-md/semibold_dc00ef defaultColor_e42ec6 name_fd6364').text
        channel_name = soup.find('h1',
                                 class_='defaultColor_a595eb heading-md/semibold_dc00ef defaultColor_e42ec6 title_fc4f04').text.split(
            ": ")[1]

        soup = soup.main

        ol_messages = soup.find("ol", class_="scrollerInner_e2e187")

        extracted_data = prompt_template | model

        # Eseguo il modello sul testo
        output = extracted_data.invoke({"text": ol_messages.text})

        logging.info(f"Risposta Ollama:\n{output}")

        # # Mi connetto alla collezione relativa al server da cui voglio estrarre i dati, se non esiste la creo
        # collection = connect_to_mongo_collection(client, server_name)
        #
        # for message in all_messages:
        #     message_to_save = {
        #         'author': message['author'],
        #         'date': message['date'],
        #         'content': message['content'],
        #         'channel_name': channel_name
        #     }
        #     save_to_mongo(message_to_save, collection)

    disconnect_to_mongo(client)
    driver.quit()


if __name__ == "__main__":
    discord_ollama_scraper()
    # TODO: gestire meglio captcha durante l'accesso a Discord web.
