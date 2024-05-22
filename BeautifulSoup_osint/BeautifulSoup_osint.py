import requests
from bs4 import BeautifulSoup
import json


# Leggi i cookie da un file JSON
def read_json(path):
    with open(path, "r") as f:
        return json.load(f)


all_cookies = read_json("twitter_cookies.json")


# I cookie di sessione estratti dal browser
cookies = {
    'auth_token': all_cookies['auth_token'],
    'ct0': all_cookies['ct0'],
    'guest_id': all_cookies['guest_id']
}

# Definire l'intestazione dell'utente per simulare un browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://twitter.com/',
    'Connection': 'keep-alive'
}

# Effettua una richiesta HTTP alla pagina di ricerca di Twitter
url = 'https://x.com/search?q=python&src=typed_query'
response = requests.get(url, headers=headers, cookies=cookies)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    # Esegui lo scraping come desiderato
    print("200")

    tweets = soup.find_all('span', {'data-testid': 'tweet'})
    print(tweets)
else:
    print(f"Errore: {response.status_code}, {response.reason} \n\n {response.text}")




# Analizza il contenuto HTML
# soup = BeautifulSoup(response.content, 'html.parser')

# Estrai i tweet (esempio: usando la classe "tweet-text")
# tweet_elements = soup.find_all(class_='tweet-text')

# Stampa i testi dei tweet
# for tweet in tweet_elements:
#    print(tweet.text)
