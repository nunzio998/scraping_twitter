import requests
import random
from utils import *

interest_groups = ["Killnet", "NoName057(16)", "Lazarus", "DarkHalo", "MustangPanda", "BlackEnergy", "BadMagic",
                   "DarkSide", "LockBit", "DopplePaymer", "RagnarLocker",
                   "REvil", "DragonFly"]

primary_keywords = ["hacker", "cyberwar", "cyber", "energy"]

secondary_keywords = ["italy", "europe", "group", "attack", "threat"]

# Connessione al database MongoDB
client = connect_to_mongo()

for group in interest_groups:
    print("in lavorazione: ", group)
    # Connessione alla collezione di  mongoDB
    collection = connect_to_mongo_collection(client, group)

    # Estraggo parametri casuali per la ricerca
    extracted_primary_keyword = random.choice(primary_keywords)
    extracted_secondary_keyword = random.choice(secondary_keywords)

    # Definisco i parametri per la richiesta
    payload = {
        "api_key": config_data['api_key'],
        "query": f'"{group} {extracted_primary_keyword} {extracted_secondary_keyword}"',
        "num": "10"
    }
    response = requests.get(
        "https://api.scraperapi.com/structured/twitter/search", params=payload
    )

    # Estraggo i dati dalla risposta JSON. Ottengo un dizionario con i dati dei tweet.
    data = response.json()

    # Estrapolo i dati e rimuovo le info superflue. Ora ho una lista di dict con i tweet.
    # Prima controllo se la ricerca ha prodotto dati
    if 'organic_results' in data.keys():
        print("Risultati trovati per il gruppo: ", group)
        data_results = data['organic_results']
    else:
        # Se non ci sono dati, passo al gruppo successivo
        print("Nessun risultato utile per il gruppo: ", group)
        continue

    # Inserisco i tweet nel database
    save_to_mongo(data_results, collection)
