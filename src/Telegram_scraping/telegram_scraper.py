"""
Questo script ha il compito di effettuare lo scraping di dati da Telegram. Tale obbiettivo viene perseguito tramite
l'apposita libreria Python Telegram, 'telethon'. Questa permette all'utente di utilizzare le api della piattaforma e di
avere quindi accesso ai contenuti dei canali o dei gruppi che l'utente sceglie si specificare o che sono presenti in una
lista target che viene mantenuta su MongoDB. In questa modalità, quindi, i dati vengono facilmente estratti, trattati e
infine salvati su un apposito DB.\n

Autore: Francesco Pinsone
"""
import argparse
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import logging
from src.Telegram_scraping.utils.utils import read_json, connect_to_mongo, connect_to_mongo_collection, \
    disconnect_to_mongo, save_to_mongo


# De-commentare per avviare lo script da riga di comando
# from utils.utils import read_json, connect_to_mongo, connect_to_mongo_collection, disconnect_to_mongo, save_to_mongo

async def telegram_scraper(m_client, channel_group):
    """
    Funzione principale per il recupero dei messaggi da un canale Telegram.\n
    Una volta avviato il client Telegram viene acquisita una cronologia dei messaggi del canale d'interesse.
    Tali messaggi vengono poi filtrati tramite l'utilizzo di keywords che possono variare di volta in volta in base
    alla ricerca. Viene poi effettuata una pulizia dei dati filtrati per selezionare i campi che contengono
    maggior contenuto informativo. Infine i dati vengono salvati su un apposito DB.\n
    :param m_client: oggetto che identifica il client di mongoDB\n
    :param channel_group: nome del canale Telegram\n
    :return: None
    """
    # TODO: Aggiungere limite temporale durante lo scaricamento dei messaggi. Valutare l'utilizzo del campo date all'interno di ogni messaggio che viene scaricato.
    # Avviare il client
    await client.start()
    print("Client avviato")

    collection = connect_to_mongo_collection(m_client, channel_group)

    # Ottenere l'entità del canale
    channel = await client.get_entity(channel_group)

    # Richiedere la cronologia dei messaggi
    offset_id = 0
    limit = 100  # Numero di messaggi da scaricare per ogni richiesta
    all_messages = []

    while True:
        history = await client(GetHistoryRequest(
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
    limit = 1000
    counter_messages = 0
    for message in all_messages:
        logging.info(message.to_dict())
        message_data = message.to_dict()

        # Ottieni informazioni sul mittente
        sender = None
        if message.from_id:  # Verifica se il messaggio ha un mittente
            try:
                sender = await client.get_entity(message.from_id)
                sender_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip()  # Nome e cognome
                sender_username = sender.username  # Username, se disponibile
                message_data['sender_name'] = sender_name
                message_data['sender_username'] = sender_username
            except Exception as e:
                logging.error(f"Errore nell'ottenere informazioni sul mittente: {e}")

        # Rimuovi i campi indesiderati
        fields_to_remove = ['out', 'media_unread', 'silent', 'from_scheduled', 'legacy', 'edit_hide', 'pinned',
                            'noforwards', 'invert_media', 'offline', 'from_boosts_applied', 'via_bot_id',
                            'via_business_bot_id', 'reply_markup', 'grouped_id', 'restriction_reason', 'ttl_period',
                            'quick_reply_shortcut_id', 'effect', 'factcheck']
        # TODO: Studio di significatività dei campi da rimuovere più approfondito
        for field in fields_to_remove:
            message_data.pop(field, None)  # Usa pop per rimuovere il campo, se esiste

        logging.info(message_data)

        save_to_mongo(message_data, collection)

        # Incremento il contatore dei messaggi e controllo se ho raggiunto il limite
        counter_messages += 1
        if counter_messages >= limit:
            break


if __name__ == "__main__":
    # Configuro il logger
    logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                        format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log

    # credenziali API
    credentials = read_json("utils/credentials.json")

    api_id = credentials["api_id"]
    api_hash = credentials["api_hash"]
    phone = credentials["phone"]

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
        print("NO TARGET")
        targets_collection = connect_to_mongo_collection(mongo_client, "targets")
        documents = targets_collection.find()
        target_list = [doc['target_name'] for doc in documents]

    # Avvio del client Telegram e scraping
    with client:
        for target in target_list:
            client.loop.run_until_complete(telegram_scraper(mongo_client, target))

    # Disconnessione dal DB
    disconnect_to_mongo(mongo_client)

    with client:
        for target in target_list:
            client.loop.run_until_complete(telegram_scraper(mongo_client, target))

    disconnect_to_mongo(mongo_client)
