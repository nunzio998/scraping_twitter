"""
Il seguente script fornisce la funzione di supporto per effettuare un check sulla presenza di deepfake nelle immagini raccolte durante lo scraping su X.\n
Lo script utilizza una delle API della piattaforma Sightengine, alla quale è quindi necessario registrarsi prima di poterlo utilizzare.\n
Il link per la registrazione è il seguente: 'https://dashboard.sightengine.com/signup'. Una volta effettuata la registrazione sarà necessario inserire le
proprie credenziali api nel file json presente nella cartella 'utils'.

Autore: Francesco Pinsone.
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


credentials_api = read_json("/Users/francesco/Documents/Campus Biomedico/2 anno/II Semestre/Tesi/python_workspace/src/X_scraping/chrome/deepfake_detection/utils/credentials_api.json")


def detect_image(image_url) -> bool:
  """
  Questa funzione ha lo scopo di effettuare un check su un immagine di cui si possiede l'url per verificare se quest'ultima sia reale o sia AI Generated.
  Ritorna quindi True se l'immagine è un deepfake o False se non lo è.\n
  :param image_url: string, url dell'immagine che voglio controllare\n
  :return: bool
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
