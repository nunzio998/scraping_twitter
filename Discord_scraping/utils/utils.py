import json
import re
import time

import pymongo
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def read_json(path):
    with open(path, 'r') as file:
        return json.load(file)


config_data = read_json('utils/credentials.json')


# Funzioni MongoDB:
def connect_to_mongo():
    connection_string = config_data['connection_string']
    client = pymongo.MongoClient(connection_string)
    # Provo a connettermi al database
    try:
        client.admin.command('ping')
        print("Connesso al database: ", client.server_info()["version"])
    except Exception as e:
        print(e)

    return client


def disconnect_to_mongo(client):
    print("Disconnesso dal database: ", client.server_info()["version"])
    client.close()


def connect_to_mongo_collection(client, collection_name):
    db = client.get_database(config_data['database'])

    # Verifica se la collezione esiste già
    if collection_name not in db.list_collection_names():
        # Se la collezione non esiste, creala
        db.create_collection(collection_name)
        print("Creata la collezione:", collection_name)
    else:
        print("La collezione esiste già:", collection_name)

    return db.get_collection(collection_name)


def save_to_mongo(data, collection):
    collection.insert_one(data)


def beautifulsoup_analisys(driver, scroll_times):
    all_messages = []

    # Scorri verso l'alto per caricare più messaggi e salva i nuovi messaggi
    for _ in range(scroll_times):
        scroll_up(driver, 1)

        # Estraggo HTML pagina con BeautifulSoup
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        soup = soup.body

        # Trova nome server e nome canale
        server_name = soup.find('h2', class_='defaultColor_a595eb lineClamp1_a595eb text-md/semibold_dc00ef defaultColor_e9e35f name_fd6364').text
        channel_name = soup.find('h1', class_='defaultColor_a595eb heading-md/semibold_dc00ef defaultColor_e9e35f title_fc4f04').text.split(': ')[1]

        # Trova tutti i messaggi
        messages = soup.find_all('div', class_='contents_f9f2ca')

        for message in messages:
            # Trovo autore e data. Se non trovo l'autore vuol dire che l'autore è lo stesso del messaggio precedente quindi resta invariato
            if message.find('span', class_='username_f9f2ca desaturateUserColors_c7819f clickable_f9f2ca'):
                author = message.find('span', class_='username_f9f2ca desaturateUserColors_c7819f clickable_f9f2ca').text

            timestamp = message.find('time')['datetime']

            # Trovo il contenuto del messaggio
            content = message.find('div', class_='markup_f8f345 messageContent_f9f2ca').text
            # Se la stringa è vuota, salta il messaggio (non lo salva)
            if re.fullmatch(r'\n*', content):
                continue
            all_messages.append({'author': author, 'date': timestamp, 'content': content})

    return all_messages, server_name, channel_name


# Funzione per scorrere verso l'alto e caricare più messaggi
def scroll_up(driver, times):
    for _ in range(times):
        page = driver.find_element(By.TAG_NAME, 'html')
        page.send_keys(Keys.PAGE_UP)
        time.sleep(2)  # Aspetta che i messaggi vengano caricati
