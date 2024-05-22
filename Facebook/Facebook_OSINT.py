import requests


def extract_facebook_posts(page_url, access_token):
    # Costruisci l'URL per ottenere i post della pagina utilizzando l'API Graph di Facebook
    api_url = f"{page_url}/posts?access_token={access_token}"

    # Esegui la richiesta HTTP GET all'API Graph di Facebook
    response = requests.get(api_url)

    # Verifica se la richiesta ha avuto successo
    if response.status_code == 200:
        # Estrai i dati dalla risposta JSON
        data = response.json()

        # Verifica se ci sono post nella risposta
        if 'data' in data:
            # Itera sui post e stampa il loro contenuto
            for post in data['data']:
                print(post.get('message', ''))
        else:
            print("Nessun post trovato.")
    else:
        print(f"Errore {response.status_code}: Impossibile ottenere i post.")


# URL della pagina Facebook da cui estrarre i post
page_url = "https://www.facebook.com/groups/964488645244440/?hoisted_section_header_type=recently_seen" \
           "&multi_permalinks=978524953840809 "

# Token di accesso valido per l'accesso all'API Graph di Facebook
access_token = "EAAN5Hob5v3gBOyJ2pfGZCFLkaATFhdSp9FP2cKgKI2CrubdfGTO9fjjVGE4fyEYDDkdmr1MKDYQ4DczwsvXsgR7F7VxYfKFObvDaH8ZBkZAB3yuUgcUBDV5pZAeThZAw9Mo7oBclEw7TAjC16J08HFjNKJsRo4vZC9kuDt1l3HgZANzwtpRXch1RLuvDdTiQcRtS6ZC1KSfNzPUsIyC86qoZD "

# Chiama la funzione per estrarre i post dalla pagina Facebook
extract_facebook_posts(page_url, access_token)
