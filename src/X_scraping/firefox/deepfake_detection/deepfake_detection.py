"""
Questo script consente di verificare se un'immagine è stata generata da un'intelligenza artificiale (deepfake) o è una fotografia reale,
utilizzando il servizio API offerto da Sightengine. È progettato come supporto per analizzare immagini raccolte durante operazioni di scraping su X (Twitter).

**Funzionalità principali:**\n
1. **Lettura delle credenziali API:** Le credenziali necessarie per accedere al servizio Sightengine vengono lette da un file JSON presente nella cartella `utils`.\n
2. **Analisi delle immagini:** Tramite la funzione `detect_image`, lo script invia l'URL di un'immagine all'API e interpreta i risultati per classificare l'immagine come reale o generata da AI.\n
3. **Configurazione semplice:** La funzione `read_json` semplifica l'importazione di credenziali o altre configurazioni memorizzate in formato JSON.\n

**Prerequisiti:**\n
- È necessario registrarsi su Sightengine per ottenere le credenziali API (link per la registrazione: `https://dashboard.sightengine.com/signup`).\n
- Salvare le credenziali (`api_user` e `api_secret`) in un file JSON nella posizione indicata (`utils/credentials_api.json`).\n

**Componenti principali:**\n
- **`read_json`:** Funzione di supporto per leggere file JSON, utilizzata per caricare le credenziali API.\n
- **`detect_image`:** Funzione principale che invia una richiesta all'API di Sightengine e restituisce un valore booleano che indica se l'immagine è un deepfake.\n

**Flusso di utilizzo:**\n
1. L'utente registra un account su Sightengine e ottiene le credenziali API.\n
2. Le credenziali vengono salvate nel file JSON configurato.\n
3. La funzione `detect_image` viene chiamata con l'URL di un'immagine, e lo script restituisce:\n
   - `True`: se l'immagine è classificata come deepfake.\n
   - `False`: se l'immagine è reale.\n

**Autore:** Francesco Pinsone
"""
import requests
import json


def read_json(path):
  """
  Funzione per la lettura di file JSON.\n
  :param path: percorso del file JSON\n
  :return: dict, contenuto del file JSON
  """
  with open(path, 'r') as file:
    return json.load(file)


credentials_api = read_json("/Users/francesco/Documents/Campus Biomedico/2 anno/II Semestre/Tesi/python_workspace/src/X_scraping/firefox/deepfake_detection/utils/credentials_api.json")


def detect_image(image_url) -> bool:
  """
  La funzione `detect_image` verifica se un'immagine, accessibile tramite un URL, è stata generata da un'intelligenza artificiale (deepfake) 
  o è una fotografia reale, utilizzando un'API esterna per l'analisi.
  
  **Comportamento della funzione:**\n
  1. Effettua una richiesta GET all'API specificando i parametri richiesti, come l'URL dell'immagine e le credenziali API.\n
  2. Analizza la risposta dell'API, che fornisce un punteggio per la probabilità che l'immagine sia generata da AI.\n
  3. Confronta il valore del parametro `ai_generated` con una soglia (0.5) per determinare il risultato:\n
     - Se il valore supera 0.5, l'immagine viene classificata come deepfake.\n
     - Se il valore è inferiore o uguale a 0.5, l'immagine è considerata reale.\n

  :param **image_url**: string, url dell'immagine da controllare\n
  :return: **bool**, True se l'immagine è deepfake, False se è reale
  """""

  params = {
    'url': image_url,
    'models': 'faces,genai',
    'api_user': credentials_api["api_user"],
    'api_secret': credentials_api["api_secret"]
  }

  r = requests.get('https://api.sightengine.com/1.0/check.json', params=params)

  output = json.loads(r.text)

  if output["type"]["ai_generated"] > 0.5:
    return True  # L'immagine è deepfake
  else:
    return False  # L'immagine non è deepfake
