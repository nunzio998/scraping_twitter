import json
import re
from datetime import datetime


# Leggo il file e divido i post
def read_posts_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        # creo una lista che contiene tutte le righe del file
        lines = file.readlines()
        print(lines)

    posts = []  # lista che conterrà tutti i post
    post = []  # lista di appoggio temporanea per salvare le righe di un post

    for i in range(0, len(lines)):
        # controllo se lines[i] è l'ultimo elemento della lista
        stripped_line = lines[i].strip()

        if i == len(lines) - 1:
            post.append(stripped_line)
            posts.append(post)
            break  # esco dal ciclo for

        # controllo che il carattere in cui mi trovo non sia il primo di un nuovo post.
        # se cosi fosse il carattere successivo sarà un tag_username e quindi inizierà con '@'. In tal caso non aggiungo a post e vado avanti
        if (not lines[i + 1].strip()[0] == '@') or i == 0:
            post.append(stripped_line)
        else:  # ho letto un intero post
            posts.append(post)
            post = [stripped_line]  # resetto la lista di appoggio per il prossimo post
    print(posts)
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
    contenuto = ' '.join(line.strip() for line in contenuto_lines if not re.match(r'^\d+(\.\d+)?$', line.strip()))

    url = lines[-1].strip()

    # Ritorno il post in formato json
    return {
        'username': username,
        'username_tag': username_tag,
        'data_pubblicazione': data_pubblicazione,
        'contenuto': contenuto,
        'url': url
    }


def read_parse_save(file_path_in, file_path_out):
    posts_lines = read_posts_from_file(file_path_in)

    parsed_posts = []  # lista che conterrà tutti i post parsati in formato json

    # Parso ogni post e lo aggiungo alla lista parsed_posts
    for post_lines in posts_lines:
        parsed_post = parse_post(post_lines)
        if parsed_post:
            parsed_posts.append(parsed_post)

    # salvo la lista di post parsati in un file json
    with open(file_path_out, 'w', encoding='utf-8') as json_file:
        json.dump(parsed_posts, json_file, ensure_ascii=False, indent=4)