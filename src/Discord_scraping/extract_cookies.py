"""
Lo script ha il compito di estrarre i cookies da una sessione Firefox nella quale l'utente ha effettuato manualmente il login
a Discord e quindi anche superato un eventuale test captcha.\n

Autore: Francesco Pinsone.\n
"""
import json
from selenium import webdriver
import logging
from utils.utils import read_json
from discord_selenium_scraper import discord_login


def extract_cookies():
    """
    La funzione permette all'utente di effettuare il login manualmente e successivamente salva i cookies di sessione
    in un file json in modo che possano essere riutilizzati in futuro.\n
    :return: None
    """
    # Configuro il logger
    logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                        format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log

    credentials = read_json("utils/conf.json")

    # Eseguo il login manualmente, poi salvo i cookies
    driver = webdriver.Firefox()

    discord_login(driver, logging, credentials)

    input("Dopo aver risolto il captcha, se presente, premi invio per continuare...")

    cookies = driver.get_cookies()
    logging.info(f"Cookies salvati: {cookies}")
    with open("utils/cookies.json", "w") as file:
        json.dump(cookies, file)

    driver.quit()


if __name__ == "__main__":
    extract_cookies()
