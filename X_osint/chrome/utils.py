import json
import re
from datetime import datetime
import pymongo

interest_groups = ["Killnet", "NoName057(16)", "Lazarus", "DarkHalo", "MustangPanda", "BlackEnergy", "BadMagic",
                   "DarkSide", "LockBit", "DopplePaymer", "RagnarLocker",
                   "REvil", "DragonFly"]

primary_keywords = ["hacker", "cyberwar", "cyber", "energy"]

secondary_keywords = ["italy", "europe", "group", "attack", "threat"]

def read_json(path):
    with open(path, 'r') as file:
        return json.load(file)


config_data = read_json('mongo_utils.json')


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
    print("Salvato nel database: ", data['url'])


# config_data = read_json('mongo_utils.json')

# Leggo il file e divido i post
def read_posts(filtered_lines):
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

        # controllo che il carattere in cui mi trovo non sia il primo di un nuovo post.
        # se cosi fosse il carattere successivo sarà un tag_username e quindi inizierà con '@'. In tal caso non aggiungo a post e vado avanti
        if (not filtered_lines[i + 1].strip()[0] == '@') or i == 0:
            post.append(stripped_line)
        else:  # ho letto un intero post
            posts.append(post)
            post = [stripped_line]  # resetto la lista di appoggio per il prossimo post
    return posts


# Prende la lista contenente i post e estrare da questi solo le info utili in formato json
def parse_post(lines):
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

    # L'ultimo elemento sarà l'url del post, altrimenti scarto il post.
    if lines[-1].strip().startswith('https://'):
        url = lines[-1].strip()
    else:
        return None

    # Ritorno il post in formato json
    return {
        'username': username,
        'username_tag': username_tag,
        'data_pubblicazione': data_pubblicazione,
        'contenuto': contenuto,
        'commenti': commenti,
        'repost': repost,
        'like': like,
        'visualizzazioni': visualizzazioni,
        'url': url
    }


def read_parse_save(posts_to_save, group_name, client):
    posts_lines = read_posts(posts_to_save)

    # Connessione alla collezione dati
    collection = connect_to_mongo_collection(client, group_name)

    # Parso ogni post e lo aggiungo al database
    for post_lines in posts_lines:
        parsed_post = parse_post(post_lines)

        # Salvo il post parsato nel database
        if parsed_post:
            save_to_mongo(parsed_post, collection)
