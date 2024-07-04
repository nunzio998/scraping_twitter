from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
import asyncio
from utils import read_json, connect_to_mongo, connect_to_mongo_collection, disconnect_to_mongo, save_to_mongo

# Le tue credenziali API

credentials = read_json("utils/credentials.json")

api_id = credentials["api_id"]
api_hash = credentials["api_hash"]
phone = credentials["phone"]

# Nome del canale da cui fare scraping
channels_username = ['MinisteroSalute', 'VoodooHardware']

# Creare il client
client = TelegramClient('session_name', api_id, api_hash)


async def main(m_client, channel_group):
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
        all_messages.extend(messages)
        offset_id = messages[-1].id

    # Stampo i messaggi
    for message in all_messages:
        print(message.to_dict())
        save_to_mongo(message.to_dict(), collection)

mongo_client = connect_to_mongo()

with client:
    for channel in channels_username:
        client.loop.run_until_complete(main(mongo_client, channel))

disconnect_to_mongo()