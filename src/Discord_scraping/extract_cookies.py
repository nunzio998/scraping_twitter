"""
Lo script ha il compito di estrarre i cookies da una sessione Firefox nella quale l'utente ha effettuato manualmente il login
a Discord e quindi anche superato un eventuale test captcha.\n

Autore: Francesco Pinsone.\n
"""
import json
from selenium import webdriver


def extract_cookies():
    """
    La funzione permette all'utente di effettuare il login manualmente e successivamente salva i cookies di sessione
    in un file json in modo che possano essere riutilizzati in futuro.\n
    :return: None
    """
    # Eseguo il login manualmente, poi salvo i cookies
    driver = webdriver.Firefox()
    driver.get("https://discord.com/login")

    input("Effettua il login, poi premi Invio per continuare...")

    cookies = driver.get_cookies()
    with open("utils/cookies.json", "w") as file:
        json.dump(cookies, file)

    driver.quit()


if __name__ == "__main__":
    extract_cookies()
