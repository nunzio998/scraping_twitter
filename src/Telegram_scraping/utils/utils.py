"""
Questo script definisce e ospita una serie di funzioni utili per l'integrazione e la gestione di operazioni su Telegram e MongoDB.
Le funzionalità incluse sono modulari e possono essere richiamate da altri script. Ecco una panoramica delle principali funzioni:

- **Gestione MongoDB**: Connessione, creazione di collezioni, salvataggio e disconnessione dal database.
- **Interazioni con Telegram**: Verifica dell'esistenza di username/canali/gruppi.
- **Gestione e parsing dei dati**: Controllo delle date e formattazione dei dati in ingresso.
- **Utilità generali**: Lettura di file JSON di configurazione.

Autore: Francesco Pinsone
"""
import json
import pymongo
import logging
from telethon.errors.rpcerrorlist import UsernameInvalidError, UsernameNotOccupiedError
from datetime import datetime, timezone

# Configuro il logger
logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                    format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log


def read_json(path):
    """
    Funzione per la lettura di file JSON.\n
    :param path: percorso del file JSON\n
    :return: dict, contenuto del file JSON
    """
    with open(path, 'r') as file:
        return json.load(file)


config_data = read_json('/Users/francesco/Documents/Campus Biomedico/2 anno/II Semestre/Tesi/python_workspace/src/Telegram_scraping/utils/conf.json')


# Funzioni MongoDB:
def connect_to_mongo():
    """
    Funzione che consente di connettersi al database MongoDB.\n
    :return: client, oggetto che rappresenta la connessione al database
    """
    connection_string = config_data['connection_string']
    client = pymongo.MongoClient(connection_string)
    # Provo a connettermi al database
    try:
        client.admin.command('ping')
        logging.info(f"Connesso al database: {client.server_info()['version']}")
    except Exception as e:
        logging.exception(e)

    return client


def disconnect_to_mongo(client):
    """
    Funzione che consente di disconnettersi dal database MongoDB.\n
    :param client: oggetto che rappresenta la connessione al database\n
    :return: None
    """
    logging.info(f"Disconnesso dal database: {client.server_info()['version']}")
    client.close()


def connect_to_mongo_collection(client, collection_name):
    """
    Funzione che consente di connettersi ad una specifica collezione del database MongoDB, oppure di crearla se non esiste.\n
    :param client: oggetto che rappresenta la connessione al database\n
    :param collection_name: stringa, nome della collezione\n
    :return: collection, oggetto che rappresenta la collezione
    """
    db = client.get_database(config_data['database'])

    # Verifica se la collezione esiste già
    if collection_name not in db.list_collection_names():
        # Se la collezione non esiste, creala
        db.create_collection(collection_name)
        logging.info(f"Creata la collezione:{collection_name}")
    else:
        logging.info(f"La collezione esiste già: {collection_name}")

    return db.get_collection(collection_name)


def save_to_mongo(data, collection):
    """
    Funzione per il salvataggio di dati nel database MongoDB.\n
    :param data: dict, dati da salvare\n
    :param collection: oggetto che rappresenta la collezione\n
    :return: None
    """
    collection.insert_one(data)
    logging.info(f"Salvato nel database:{data['id']}")


async def check_username_existence(client, username):
    """
    La funzione check_username_existence verifica se uno username specificato esiste su Telegram. Si occupa di gestire
    automaticamente la formattazione dello username, aggiungendo il carattere '@' se assente. Utilizzando il metodo
    get_entity del client Telethon, tenta di recuperare l'entità associata allo username. In caso di successo, conferma
    l'esistenza dello username restituendo True. Se lo username è invalido o non è occupato, gestisce l'eccezione e
    restituisce False. È utile per controllare la validità di canali o gruppi prima di procedere con ulteriori
    operazioni.\n

    :param client: Istanza del client Telethon da utilizzare per la verifica.\n
    :param username: Username o link del canale/gruppo Telegram da verificare.\n
    :return: True se lo username esiste su Telegram, False altrimenti.
    """
    try:
        # Controllo formattazione username
        if not username.startswith("@"):
            username = f"@{username}"  # Aggiunge '@' se mancante

        # Verifico l'esistenza dell'entità
        entity = await client.get_entity(username)
        # print(f"Username valido: {entity.title if hasattr(entity, 'title') else entity.username}")
        return True
    except (UsernameInvalidError, UsernameNotOccupiedError):
        # print(f"Errore: lo username '{username}' non esiste o non è valido.")
        return False


def check_date(date, limit_date):
    """
    La funzione check_date confronta la data di un messaggio con una data limite per determinare se il messaggio è stato
    inviato prima della data specificata. Gestisce formati di data diversi e converte eventuali date senza fuso orario
    (offset-naive) in date con fuso orario (offset-aware) in formato UTC. Se le date non sono già in formato datetime,
    le converte da stringhe nei rispettivi formati. Restituisce True se la data del messaggio è antecedente alla data limite,
    altrimenti restituisce False.\n

    :param date: Data del messaggio, che può essere un oggetto datetime o una stringa ISO.\n
    :param limit_date: Data limite per il confronto, che può essere un oggetto datetime o una stringa nel formato "dd-mm-YYYY".\n
    :return: True se la data del messaggio è precedente alla data limite, False altrimenti.
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
