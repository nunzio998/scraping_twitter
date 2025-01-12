"""
Questo script permette l'estrazione automatizzata di messaggi da canali e gruppi Telegram e il loro salvataggio in un
database MongoDB. Utilizza la libreria Telethon per connettersi alle API di Telegram e MongoDB per archiviare i dati,
offrendo un sistema flessibile, configurabile e resiliente adatto a diversi scenari di utilizzo.

Caratteristiche principali:\n
----------------------------
1. **Connessione a Telegram**:\n
   - Recupero della cronologia dei messaggi da canali o gruppi specificati.\n
   - Estrazione di dettagli sui mittenti (nome, cognome, username), se disponibili.\n
2. **Gestione e archiviazione dei dati**:\n
   - Salvataggio dei messaggi in collezioni MongoDB organizzate per canale o gruppo.\n
   - Pulizia e filtraggio dei dati per rimuovere campi ridondanti o non rilevanti.\n
3. **Configurabilità**:\n
   - Parametri come credenziali API, data limite (`limit_date`) e numero massimo di tentativi sono configurabili tramite un file JSON.\n
   - Supporto per specificare target tramite linea di comando oppure caricandoli da una collezione "targets" in MongoDB.\n
4. **Robustezza e resilienza**:\n
   - Gestione degli errori di connessione con tentativi di riconnessione configurabili.\n
   - Logging dettagliato per monitorare l'intero processo e facilitare il debugging.\n
5. **Esecuzione asincrona**:\n
   - Utilizzo di funzioni asincrone per garantire efficienza nelle operazioni I/O intensive, come l'interazione con le API di Telegram e il database.\n
6. **Supporto CLI**:\n
   - Permette l'inserimento dei target direttamente da linea di comando tramite il parametro `--targets`.\n
   - Se i target non vengono forniti, vengono automaticamente caricati dal database MongoDB.\n

Flusso di esecuzione:\n
----------------------
1. **Configurazione iniziale**:\n
   - Lettura delle credenziali API e dei parametri di configurazione da un file JSON.\n
   - Configurazione del logger per monitorare tutte le operazioni.\n
2. **Identificazione dei target**:\n
   - Recupero dei target specificati tramite linea di comando o dalla collezione "targets" in MongoDB.\n
3. **Estrazione dei messaggi**:\n
   - Connessione ai canali o gruppi specificati.\n
   - Scaricamento della cronologia dei messaggi e arricchimento con informazioni sui mittenti.\n
   - Filtraggio dei dati per rispettare eventuali limitazioni temporali (`limit_date`).\n
4. **Salvataggio dei dati**:\n
   - Archiviazione dei messaggi estratti in MongoDB, all'interno di collezioni corrispondenti ai canali o gruppi di origine.\n
5. **Chiusura delle connessioni**:\n
   - Al termine dell'elaborazione, il client Telegram viene chiuso e la connessione a MongoDB viene terminata.\n

Prerequisiti:\n
-------------
- Una configurazione valida delle credenziali API di Telegram (api_id, api_hash, phone).\n
- Una connessione funzionante al database MongoDB.\n
- La libreria Telethon installata.\n

**Autore**: Francesco Pinsone.
"""
import argparse
import asyncio

from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import logging
from src.Telegram_scraping.utils.utils import read_json, connect_to_mongo, connect_to_mongo_collection, disconnect_to_mongo, save_to_mongo, check_date, check_username_existence


# De-commentare per avviare lo script da riga di comando
# from utils.utils import read_json, connect_to_mongo, connect_to_mongo_collection, disconnect_to_mongo, save_to_mongo


async def channel_scraper(t_client, m_client, channel_group, limit_date, max_retries=5):
    """
    La funzione `channel_scraper` estrae, elabora e memorizza i messaggi provenienti da un canale o gruppo Telegram
    nel database MongoDB. È progettata per gestire una vasta gamma di scenari, come l'estrazione basata su una data limite,
    il recupero delle informazioni del mittente (se disponibili), e la gestione degli errori e delle riconnessioni in caso
    di interruzioni.

    **Funzionalità principali**:\n
    1. **Connessione al Client Telegram e MongoDB**:\n
        - La funzione stabilisce una connessione asincrona con il client Telegram (`t_client`) e con la collezione MongoDB associata al canale o gruppo target (`channel_group`).\n
    2. **Recupero dei Messaggi**:\n
        - Utilizza il metodo `GetHistoryRequest` per scaricare la cronologia dei messaggi dal canale o gruppo specificato.\n
        - I messaggi vengono raccolti iterativamente, con un limite configurabile sul numero di messaggi per ogni richiesta.\n
        - Viene implementato un controllo sulla data dei messaggi, escludendo quelli precedenti alla data limite (`limit_date`).\n
    3. **Elaborazione e Filtraggio dei Messaggi**:\n
        - I messaggi sono convertiti in formato dizionario e arricchiti con informazioni aggiuntive, come:\n
            - Nome e cognome del mittente (se disponibili).\n
            - Username del mittente.\n
            - Nome del canale o gruppo da cui il messaggio è stato estratto.\n
        - Sono rimossi campi non essenziali o ridondanti dai dati dei messaggi per mantenere solo quelli rilevanti.\n
        - La funzione include un elenco predefinito di campi da rimuovere e supporta un'ulteriore analisi della loro utilità.\n
    4. **Gestione degli Errori e dei Tentativi**:\n
        - In caso di interruzioni di rete o altri errori di connessione, la funzione tenta automaticamente di ristabilire la connessione fino a un massimo di `max_retries` volte.\n
        - In caso di superamento del limite di tentativi, l'errore viene sollevato per consentire una gestione esterna.\n
    5. **Memorizzazione dei Dati**:\n
        - I dati elaborati vengono salvati nella collezione MongoDB corrispondente al canale o gruppo target, utilizzando la funzione `save_to_mongo`.\n
    6. **Logging**:\n
        - La funzione registra dettagliatamente le operazioni effettuate e i dati elaborati, inclusi eventuali errori, per agevolare il debugging.\n

    :param t_client (TelegramClient): Istanza del client Telegram.
    :param m_client (MongoClient): Istanza del client MongoDB.
    :param channel_group (str): Nome del canale o gruppo Telegram target.
    :param limit_date (datetime): Data limite per considerare i messaggi (escludendo quelli più vecchi).
    :param max_retries (int): Numero massimo di tentativi di riconnessione in caso di errori (predefinito: 5).
    :return: Nessun valore restituito.\n
    """
    retries = 0

    while retries < max_retries:
        try:
            # TODO: Aggiungere limite temporale durante lo scaricamento dei messaggi. Valutare l'utilizzo del campo date all'interno di ogni messaggio che viene scaricato.
            # Avviare il client
            await t_client.start()
            logging.info("Client avviato")

            collection = connect_to_mongo_collection(m_client, channel_group)

            # Ottenere l'entità del canale
            channel = await t_client.get_entity(channel_group)

            # Richiedere la cronologia dei messaggi
            offset_id = 0
            limit = 5  # Numero di messaggi da scaricare per ogni richiesta
            all_messages = []

            while True:
                history = await t_client(GetHistoryRequest(
                    peer=channel,
                    offset_id=offset_id,
                    offset_date=None,
                    add_offset=0,
                    limit=limit,
                    max_id=0,
                    min_id=0,
                    hash=0
                ))

                if not history.messages:
                    break

                messages = history.messages

                # Filtro i messaggi in modo che vengano selezionati solo quelli che contengono una delle parole chiave specificate
                all_messages.extend(messages)
                offset_id = messages[-1].id

            # Stampo i messaggi
            counter_messages = 0
            for message in all_messages:
                # Controllo se il messaggio è più vecchio di una certa data specificata
                if check_date(message.date, limit_date):
                    break

                logging.info(message.to_dict())
                message_data = message.to_dict()

                # Ottieni informazioni sul mittente
                sender = None
                if message.from_id:  # Verifica se il messaggio ha un mittente
                    try:
                        sender = await t_client.get_entity(message.from_id)
                        sender_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip()  # Nome e cognome
                        sender_username = sender.username  # Username, se disponibile
                        message_data['sender_name'] = sender_name
                        message_data['sender_username'] = sender_username
                        message_data['channel'] = channel_group
                    except Exception as e:
                        message_data['channel'] = channel_group
                        logging.error(
                            f"Errore nell'ottenere informazioni sul mittente: {e}.\n Probabilmente si tratta di un canale e non di un gruppo.\n")

                # Rimuovi i campi indesiderati
                fields_to_remove = ['out', 'media_unread', 'silent', 'from_scheduled', 'legacy', 'edit_hide', 'pinned',
                                    'noforwards', 'invert_media', 'offline', 'from_boosts_applied', 'via_bot_id',
                                    'via_business_bot_id', 'reply_markup', 'grouped_id', 'restriction_reason',
                                    'ttl_period',
                                    'quick_reply_shortcut_id', 'effect', 'factcheck']
                # TODO: Studio di significatività dei campi da rimuovere più approfondito
                for field in fields_to_remove:
                    message_data.pop(field, None)  # Usa pop per rimuovere il campo, se esiste

                logging.info(message_data)

                save_to_mongo(message_data, collection)
            break
        except ConnectionError as e:
            retries += 1
            print(f"Errore di connessione. Tentativo {retries}/{max_retries}")
            if retries < max_retries:
                await asyncio.sleep(10)  # Attendi prima di ritentare
            else:
                raise e  # Rilancia l'errore dopo i tentativi


def telegram_scraper():
    """
    La funzione `telegram_scraper` è il punto di ingresso principale per il processo di scraping dei messaggi da uno o più
    canali o gruppi Telegram. Combina l'utilizzo di un client Telegram (basato sulla libreria `Telethon`) e di un database
    MongoDB per estrarre, elaborare e memorizzare i dati raccolti. La funzione è progettata per essere modulare, flessibile
    e configurabile tramite file JSON e argomenti da linea di comando.

    **Funzionalità principali**:\n
    1. **Configurazione del Logging**:\n
        - Inizializza un logger per registrare informazioni dettagliate sull'esecuzione, inclusi avvisi ed errori, in un formato leggibile.\n

    2. **Caricamento delle Configurazioni**:\n
        - Legge le credenziali API e altre impostazioni dal file `utils/conf.json`, incluse:\n
            - `api_id` e `api_hash` per l'autenticazione con Telegram.\n
            - `phone` per il login (se necessario).\n
            - `limit_date` per definire il limite temporale nella raccolta dei messaggi.\n
            - `max_retries` per il numero massimo di tentativi in caso di errori.\n

    3. **Gestione dei Target**:\n
        - Utilizza un parser di argomenti (`argparse`) per consentire all'utente di specificare da linea di comando uno o più target (canali o gruppi Telegram).\n
        - Se non vengono forniti target da linea di comando, li recupera automaticamente dalla collezione MongoDB `targets`.\n

    4. **Creazione e Avvio del Client Telegram**:\n
        - Crea un'istanza del client Telegram utilizzando le credenziali fornite.\n
        - Per ogni target nella lista:\n
            - Verifica l'esistenza dell'username del canale o gruppo su Telegram.\n
            - In caso di errore o username inesistente, registra un messaggio di errore e passa al prossimo target.\n
            - Avvia la funzione asincrona `channel_scraper` per eseguire l'estrazione dei messaggi da quel target.\n

    5. **Memorizzazione dei Dati**:\n
        - I dati estratti da ciascun canale o gruppo vengono elaborati e salvati nella collezione MongoDB corrispondente, mantenendo una struttura coerente.\n

    6. **Gestione delle Connessioni**:\n
        - Gestisce l'apertura e la chiusura delle connessioni al database MongoDB.\n
        - Assicura che il client Telegram venga chiuso correttamente al termine dello scraping.\n

    :return: Nessun valore restituito.
    """
    # Configuro il logger
    logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                        format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log

    # credenziali API
    credentials = read_json("utils/conf.json")

    api_id = credentials["api_id"]
    api_hash = credentials["api_hash"]
    phone = credentials["phone"]
    limit_date = credentials["limit_date"]

    # Parser per gli argomenti da linea di comando
    parser = argparse.ArgumentParser(description="Telegram scraper: estrae i dati dai canali Telegram.")
    parser.add_argument(
        "--targets",
        nargs="*",  # Accetta zero o più argomenti
        help="Elenco dei canali/gruppi Telegram da cui estrarre i messaggi (separati da spazio)."
    )
    args = parser.parse_args()

    # Creare il client Telegram
    client = TelegramClient('telegram_scraper', api_id, api_hash)

    mongo_client = connect_to_mongo()

    # Logica per ottenere i target
    if args.targets:  # Se l'utente ha specificato target da linea di comando
        target_list = args.targets
        logging.info(f"Target specificati dall'utente: {target_list}")
    else:  # Se non sono stati specificati target, caricali dal DB
        logging.info("Nessun target specificato, caricamento da MongoDB...")
        targets_collection = connect_to_mongo_collection(mongo_client, "targets")
        documents = targets_collection.find()
        target_list = [doc['target_name'] for doc in documents]

    # Avvio del client Telegram e scraping
    with client:
        for target in target_list:
            # Verifica se l'username esiste, se non esiste, passa al prossimo target
            if not check_username_existence(client, target):
                logging.error(f"Il target '{target}' non esiste su Telegram.")
                continue
            client.loop.run_until_complete(
                channel_scraper(client, mongo_client, target, limit_date, credentials["max_retries"]))

    # Disconnessione dal DB
    disconnect_to_mongo(mongo_client)


if __name__ == "__main__":
    telegram_scraper()