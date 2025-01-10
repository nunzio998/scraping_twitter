"""
Lo script consente di estrarre i cookies di sessione da un browser Firefox dopo che l'utente ha effettuato manualmente
il login a Discord, incluso il superamento di eventuali test captcha. I cookies raccolti vengono successivamente
salvati in un file JSON, permettendo di riutilizzarli in sessioni future senza la necessità di eseguire nuovamente
il login manuale.

**Autore**: Francesco Pinsone

Funzionalità principali:
- Avvia una sessione di login manuale su Discord.
- Gestisce la risoluzione di captcha se presente.
- Estrae i cookies di sessione dal browser.
- Salva i cookies in un file JSON per un utilizzo futuro.

Questo script è utile per semplificare il processo di login in esecuzioni successive, consentendo di automatizzare il login
senza dover ripetere ogni volta la procedura manuale.

"""
import json
from selenium import webdriver
import logging
from utils.utils import read_json
from src.Discord_scraping.utils.utils import login


def extract_cookies():
    """
    Questa funzione permette all'utente di effettuare il login manuale su Discord e di salvare i cookies di sessione
    in un file JSON per un uso futuro, evitando la necessità di effettuare nuovamente il login.

    La funzione esegue i seguenti passaggi:\n
    1. Configura il logger per monitorare il processo.\n
    2. Legge le credenziali di login da un file di configurazione.\n
    3. Avvia un driver del browser (Firefox) per eseguire il login su Discord.\n
    4. Permette all'utente di risolvere manualmente eventuali captcha, se presenti.\n
    5. Dopo il login, raccoglie i cookies di sessione.\n
    6. Salva i cookies in un file JSON, per poterli riutilizzare nelle sessioni future, evitando il login manuale.\n
    7. Termina la sessione del browser.\n

    La funzione è utile per memorizzare i cookies di sessione, facilitando il login automatico in future esecuzioni dello script, senza dover ripetere la procedura di login.\n

    :return: Nessun valore restituito. I cookies vengono salvati in un file JSON per un uso successivo.
    """
    # Configuro il logger
    logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                        format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log

    credentials = read_json("utils/conf.json")

    # Eseguo il login manualmente, poi salvo i cookies
    driver = webdriver.Firefox()

    login(driver, logging, credentials)

    input("Dopo aver risolto il captcha, se presente, premi invio per continuare...")

    cookies = driver.get_cookies()
    logging.info(f"Cookies salvati: {cookies}")
    with open("utils/cookies.json", "w") as file:
        json.dump(cookies, file)

    driver.quit()


if __name__ == "__main__":
    extract_cookies()
