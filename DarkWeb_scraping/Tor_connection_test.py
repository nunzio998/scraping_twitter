import requests

# Configurazione della sessione per utilizzare Tor
session = requests.Session()
session.proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

# Test di Connessione
try:
    response = session.get('http://check.torproject.org')
    print(response.text)
except requests.exceptions.RequestException as e:
    print(f"Errore di connessione: {e}")
