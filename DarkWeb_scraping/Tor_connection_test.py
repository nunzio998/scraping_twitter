import requests
import logging

# Configuro il logger
logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                    format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log

# Configurazione della sessione per utilizzare Tor
session = requests.Session()
session.proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

# Test di Connessione
try:
    response = session.get('http://check.torproject.org')
    logging.info(response.text)
except requests.exceptions.RequestException as e:
    logging.exception(f"Errore di connessione: {e}")
