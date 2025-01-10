"""
Questo script consente di effettuare lo scraping di messaggi da canali e gruppi Telegram utilizzando la libreria Telethon.
È progettato per interfacciarsi con le API di Telegram e un database MongoDB, permettendo di estrarre e salvare in modo
automatizzato i messaggi in base a determinati criteri di configurazione.

L’utente può specificare i target da cui estrarre i messaggi direttamente da linea di comando oppure utilizzare una lista
di target mantenuta in una collezione MongoDB. I messaggi vengono scaricati, elaborati per rimuovere campi ridondanti e
arricchiti con informazioni sul mittente quando disponibili. Inoltre, è possibile impostare una data limite per considerare
solo i messaggi successivi a essa.

Il processo utilizza un’architettura modulare per leggere le configurazioni, gestire le connessioni al database, e
effettuare il controllo e la verifica degli username su Telegram. È resiliente agli errori di rete, prevedendo più tentativi
di connessione configurabili. Il logger integrato garantisce il tracciamento degli eventi, degli errori e delle operazioni
effettuate, semplificando il debugging e il monitoraggio del processo. Lo script può essere eseguito direttamente e
adattato a diversi casi d’uso grazie alla sua flessibilità e configurabilità.

Autore: Francesco Pinsone
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
    La funzione channel_scraper estrae, filtra, elabora e memorizza messaggi da un canale o gruppo Telegram in un
    database MongoDB. Gestisce la connessione al client Telegram (t_client) e alla collezione MongoDB associata al
    canale di interesse, recuperando la cronologia dei messaggi tramite il metodo GetHistoryRequest. I messaggi possono
    essere filtrati in base a parole chiave e arricchiti con informazioni aggiuntive, come nome e username del mittente,
    se disponibili. È possibile definire una data limite (limit_date) per considerare solo i messaggi successivi a essa.
    La funzione rimuove campi ridondanti dai dati dei messaggi per mantenere solo quelli rilevanti, e li salva nella
    collezione MongoDB corrispondente. È progettata per essere resiliente, con una gestione dei tentativi di
    riconnessione configurabile tramite il parametro max_retries. In caso di interruzioni di rete, ritenta la
    connessione per un numero massimo di volte prima di sollevare un’eccezione. Infine, registra dettagliatamente
    eventuali errori per agevolare il debugging. Non restituisce alcun valore ma salva i dati nel database.\n
    :param t_client: client telegram\n
    :param m_client: client MongoDB\n
    :param channel_group: nome del canale target\n
    :param limit_date: data limite per estrazione messaggi\n
    :param max_retries: numero di tentativi massimi di riconnessione\n
    :return: None\n
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
    La funzione telegram_scraper gestisce il processo di scraping dei messaggi da uno o più canali o gruppi Telegram,
    utilizzando un client Telegram e un database MongoDB per memorizzare i dati. Configura un logger per registrare
    informazioni, avvisi ed errori durante l’esecuzione. Carica le credenziali API e altre configurazioni necessarie da
    un file JSON, tra cui api_id, api_hash, phone, e limit_date. Utilizza un parser di argomenti per permettere
    all’utente di specificare da linea di comando uno o più target (canali o gruppi Telegram) da cui estrarre i dati.
    Se non vengono forniti target tramite linea di comando, li recupera automaticamente da una collezione MongoDB
    chiamata “targets”.\n
    Crea un’istanza del client Telegram e si connette al database MongoDB. Per ogni target nella lista, verifica
    l’esistenza dell’username del canale o gruppo su Telegram; in caso di errore o di username inesistente, registra un
    messaggio di errore e passa al prossimo target. Avvia quindi la funzione asincrona channel_scraper per effettuare
    l’estrazione dei messaggi. Alla fine del processo, chiude la connessione al database MongoDB. La funzione utilizza
    un approccio modulare per integrare funzionalità di logging, gestione dei target e connessione ai servizi,
    rendendola flessibile e facilmente adattabile.\n
    :return: None
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
