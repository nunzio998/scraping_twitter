import json
import re
import time
from datetime import datetime

import pymongo
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

interest_groups = ["Killnet", "NoName057(16)", "Lazarus", "DarkHalo", "MustangPanda", "BlackEnergy", "BadMagic",
                   "DarkSide", "LockBit", "DopplePaymer", "RagnarLocker",
                   "REvil", "DragonFly"]

primary_keywords = ["hacker", "cyberwar", "cyber", "energy"]

secondary_keywords = ["italy", "europe", "group", "attack", "threat"]


def read_json(path):
    """
    Funzione che si occupa di leggere un file JSON.
    :param path:
    :return:
    """
    with open(path, 'r') as file:
        return json.load(file)


config_data = read_json('utils/mongo_utils.json')


def x_login(credentials_access, driver_access):
    try:
        email_field = driver_access.find_element(By.XPATH,
                                                 '/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input')
        email_field.send_keys(credentials_access["email"])
        email_field.send_keys(Keys.RETURN)
        time.sleep(2)
    except NoSuchElementException:
        print("Campo email non trovato..")

    # Controllo anche il campo username poiché dopo tanti accessi consecutivi X richiede anche lo username per sicurezza
    try:
        username_field = driver_access.find_element(By.XPATH,
                                                    '/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input')
        username_field.send_keys(credentials_access["username"])
        username_field.send_keys(Keys.RETURN)
        time.sleep(2)
    except NoSuchElementException:
        print("Campo username non trovato..")

    try:
        password_field = driver_access.find_element(By.XPATH,
                                                    '/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input')
        password_field.send_keys(credentials_access["password"])
        password_field.send_keys(Keys.RETURN)
        time.sleep(2)
    except NoSuchElementException:
        print("Campo password non trovato..")


# Funzioni MongoDB:
def connect_to_mongo():
    """
    Funzione che si occupa di connettersi al database MongoDB.
    :return:
    """
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
    """
    Funzione che si occupa di disconnettersi dal database MongoDB.
    :param client:
    :return:
    """
    print("Disconnesso dal database: ", client.server_info()["version"])
    client.close()


def get_db(client):
    """
    Funzione che ritorna il database MongoDB.
    :param client:
    :return:
    """
    return client.get_database(config_data['database'])


def connect_to_mongo_collection(client, collection_name):
    """
    Funzione che si occupa di connettersi ad una specifica collezione del database MongoDB, oppure di crearla se non esiste.
    :param client:
    :param collection_name:
    :return:
    """
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
    """
    Funzione che si occupa di il salvataggio di dati nel database MongoDB.
    :param data:
    :param collection:
    :return:
    """
    collection.insert_one(data)
    print("Salvato nel database: ", data['url'])


def save_user_info_to_mongo(data, collection):
    """
    Funzione che si occupa di il salvataggio di dati, relativi alle info utente, nel database MongoDB.
    :param data:
    :param collection:
    :return:
    """
    collection.insert_one(data)
    print("Salvato nel database: ", data['username_tag'])


# config_data = read_json('mongo_utils.json')

# Leggo il file e divido i post
def read_posts(filtered_lines):
    """
    Funzione che si occupa di leggere i post e dividerli in base al numero di righe.
    :param filtered_lines:
    :return:
    """
    posts = []  # lista che conterrà tutti i post
    post = []  # lista di appoggio temporanea per salvare le righe di un post

    for i in range(0, len(filtered_lines)):
        # controllo se lines[i] è l'ultimo elemento della lista
        stripped_line = filtered_lines[i].strip()

        # se sono all'ultimo elemento della lista, aggiungo la riga a post e poi aggiungo post a posts
        if i == len(filtered_lines) - 1:
            post.append(stripped_line)
            posts.append(post)
            break  # esco dal ciclo for

        # Controllo che il carattere in cui mi trovo non sia il primo di un nuovo post.
        # se cosi fosse il carattere successivo sarà un tag_username e quindi inizierà con '@'. In tal caso non aggiungo a post e vado avanti
        if (not filtered_lines[i + 1].strip()[0] == '@') or i == 0:
            post.append(stripped_line)
        else:  # ho letto un intero post
            posts.append(post)
            post = [stripped_line]  # resetto la lista di appoggio per il prossimo post
    return posts


# Prende la lista contenente i post e estrare da questi solo le info utili in formato json
def parse_post(lines):
    """
    Funzione che si occupa di parsare un post e restituirlo in formato json.
    :param lines:
    :return:
    """
    if len(lines) < 4:
        return None  # Skip invalid posts

    username = lines[0].strip()
    username_tag = lines[1].strip()
    data_pubblicazione = lines[3].strip()
    if len(data_pubblicazione.split()) == 2:  # Controlla se la data ha solo giorno e mese
        data_pubblicazione += f" {datetime.now().year}"

    # So che il contenuto del post si trova dalla quarta riga in poi. Utilizzando un'espressione regolare, posso ignorare le righe che contengono solo numeri.
    # Ovvero quelle righe che contengono solo il numero di like, commenti, condivisioni, ecc.
    contenuto_lines = lines[4:]
    contenuto = ' '.join(line.strip() for line in contenuto_lines if
                         not re.match(r'^\d+(\.\d+)?$', line.strip()) and not re.match(r'^https://', line.strip()))

    # Considerando tutti gli elementi di lines prendo solo quelli che contengono solo numeri e li inserisco in una lista
    numeri = [line.strip() for line in lines if re.match(r'^\d+(\.\d+)?$', line.strip())]
    if len(numeri) == 4:
        commenti = numeri[0]
        repost = numeri[1]
        like = numeri[2]
        visualizzazioni = numeri[3]
    elif len(numeri) == 3:
        commenti = None
        repost = numeri[0]
        like = numeri[1]
        visualizzazioni = numeri[2]
    elif len(numeri) == 2:
        commenti = None
        repost = None
        like = numeri[0]
        visualizzazioni = numeri[1]
    elif len(numeri) == 1:
        commenti = None
        repost = None
        like = None
        visualizzazioni = numeri[0]
    else:
        commenti = None
        repost = None
        like = None
        visualizzazioni = None

    # Creo una lista di tutti le linee che iniziano con la stringa 'https://' o 'http://'
    links = [line.strip() for line in lines if line.strip().startswith('https://') or line.strip().startswith('http://') or line.strip().startswith('blob:')]


    # Controllo che la lista non sia vuota, se lo è scarto il post
    if not links:
        return None

    # Prendo il primo link della lista, che sarà l'url del post
    url = links[0]

    # Ora, dal secondo elemento in poi, tutti gli elementi della lista che non iniziano con la stringa 'blob:' sono i link delle immagini
    # Questo perché i link che iniziano con 'blob:' sono relativi ai video.
    images = [link for link in links[1:] if not link.startswith('blob:')]

    # I link che invece iniziano con 'blob:' sono i link dei video. Vengono quindi aggiunti alla lista dei video, rimuovendo la stringa 'blob:'.
    videos = [link.replace('blob:', '') for link in links[1:] if link.startswith('blob:')]


    # Ritorno il post in formato json
    return {
        'username': username,
        'tag_username': username_tag,
        'date': data_pubblicazione,
        'content': contenuto,
        'comments': commenti,
        'reposts': repost,
        'likes': like,
        'views': visualizzazioni,
        'url': url,
        'images': images,
        'videos': videos
    }


def read_parse_save(posts_to_save, group_name, client):
    """
    Funzione che si occupa di leggere, parsare e salvare i post nel database.
    :param posts_to_save:
    :param group_name:
    :param client:
    :return:
    """
    posts_lines = read_posts(posts_to_save)

    # Connessione alla collezione dati
    collection = connect_to_mongo_collection(client, group_name)

    # Parso ogni post e lo aggiungo al database
    for post_lines in posts_lines:
        parsed_post = parse_post(post_lines)

        # Salvo il post parsato nel database, se non è None
        if parsed_post:
            save_to_mongo(parsed_post, collection)
