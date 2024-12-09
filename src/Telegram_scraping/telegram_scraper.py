"""
Questo script ha il compito di effettuare lo scraping di dati da Telegram. Tale obbiettivo viene perseguito tramite
l'apposita libreria Python Telegram, 'telethon'. Questa permette all'utente di utilizzare le api della piattaforma e di
avere quindi accesso ai contenuti dei canali ai quali l'utente è iscritto. In questa modalità, quindi, i dati
vengono facilmente estratti, trattati e infine salvati su un apposito DB.\n

Autore: Francesco Pinsone
"""
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import logging
from src.Telegram_scraping.utils.utils import read_json, connect_to_mongo, connect_to_mongo_collection, disconnect_to_mongo, save_to_mongo


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
        fields_to_remove = ['out', 'media_unread', 'silent', 'from_scheduled', 'legacy', 'edit_hide', 'pinned', 'noforwards', 'invert_media', 'offline', 'from_boosts_applied', 'via_bot_id', 'via_business_bot_id', 'reply_markup', 'grouped_id', 'restriction_reason', 'ttl_period', 'quick_reply_shortcut_id', 'effect', 'factcheck']
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

    # Nome del canale da cui fare scraping
    channels_username = ['BugCrowd', 'androidMalware', 'itarmyofukraine2022', 'noname05716', 'true_secator']

    # Creare il client
    client = TelegramClient('telegram_scraper', api_id, api_hash)

    mongo_client = connect_to_mongo()

    with client:
        for channel in channels_username:
            client.loop.run_until_complete(telegram_scraper(mongo_client, channel))