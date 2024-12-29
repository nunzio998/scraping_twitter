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
from datetime import datetime, timezone

# De-commentare per avviare lo script da riga di comando
# from utils.utils import read_json, connect_to_mongo, connect_to_mongo_collection, disconnect_to_mongo, save_to_mongo


def check_date(date, limit_date):
    """
    Funzione per controllare se la data di un messaggio è più vecchia di una certa data limite.\n
    :param date: data del messaggio\n
    :param limit_date: data limite\n
    :return: True se la data è più vecchia, False altrimenti
    """
    # print(f"Date: {date}, Limit date: {limit_date}")
    # print(f"Date type: {type(date)}, Limit date type: {type(limit_date)}")
    # Se 'date' è offset-naive, lo converti in offset-aware (UTC)
    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)

    if not isinstance(date, datetime):
        # Converto la data ISO in un oggetto datetime
        date = datetime.strptime(date[:19], "%Y-%m-%dT%H:%M:%S")  # Ignora la parte "+00:00"

    if not isinstance(limit_date, datetime):
        # Converto la data specificata in un oggetto datetime
        limit_date = datetime.strptime(limit_date, "%d-%m-%Y")

    # Rendi 'limit_date' offset-aware
    limit_date = limit_date.replace(tzinfo=timezone.utc)

    # print("-----------------------------------------------------")
    # print(f"Date: {date}, Limit date: {limit_date}")
    # print(f"Date type: {type(date)}, Limit date type: {type(limit_date)}")

    return date < limit_date

async def telegram_scraper(m_client, channel_group, limit_date):
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
    logging.info("Client avviato")

    collection = connect_to_mongo_collection(m_client, channel_group)

    # Ottenere l'entità del canale
    channel = await client.get_entity(channel_group)

    # Richiedere la cronologia dei messaggi
    offset_id = 0
    limit = 5  # Numero di messaggi da scaricare per ogni richiesta
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
                sender = await client.get_entity(message.from_id)
                sender_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip()  # Nome e cognome
                sender_username = sender.username  # Username, se disponibile
                message_data['sender_name'] = sender_name
                message_data['sender_username'] = sender_username
            except Exception as e:
                message_data['canale'] = sender.title
                logging.error(f"Errore nell'ottenere informazioni sul mittente: {e}.\n Probabilmente si tratta di un canale e non di un gruppo.\n")

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


if __name__ == "__main__":
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
            if target == "BugCrowd":
                continue
            client.loop.run_until_complete(telegram_scraper(mongo_client, target, limit_date))

    # Disconnessione dal DB
    disconnect_to_mongo(mongo_client)
