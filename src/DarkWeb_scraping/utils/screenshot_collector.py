"""
Il seguente script offre la possibilità di estrarre screenshot da siti .onion.\n
Si può eseguire lo script da riga di comando specificando gli url da cui estrarre gli screenshot.
Questi saranno poi salvati nella cartella 'screenshots' con il nome dell'url in formato png.\n
In alternativa si può utilizzare la funzione take_screenshot(url) per ottenere uno screenshot in formato binario.\n

Autore: Francesco Pinsone.\n
"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import argparse
import logging


def configure_tor_driver() -> webdriver.Firefox:
    """
    Configura il driver di Firefox per utilizzare Tor.
    """
    options = Options()
    options.add_argument("--headless")
    options.set_preference("network.proxy.type", 1)
    options.set_preference("network.proxy.socks", "127.0.0.1")
    options.set_preference("network.proxy.socks_port", 9050)
    options.set_preference("network.proxy.socks_remote_dns", True)
    driver = webdriver.Firefox(options=options)
    return driver


def take_screenshot(url, driver) -> str:
    """
    Funzione per l'estrazione di uno screenshot da un sito .onion.
    :param url: URL del sito .onion
    :param driver: WebDriver configurato (opzionale)
    :return: Screenshot in formato base64
    """

    try:
        driver.get(url)
        screenshot_data = driver.get_screenshot_as_base64()
    except Exception as e:
        raise RuntimeError(f"Errore durante lo screenshot: {e}")
    finally:
        driver.quit()

    return screenshot_data


def save_screenshot(url) -> None:
    """
    Funzione per l'estrazione di uno screenshot da un sito .onion.\n
    :param url:
    :return:
    """
    # Configura le opzioni di Firefox per utilizzare il proxy Tor
    options = Options()
    # options.headless = True
    options.add_argument("--headless")
    options.set_preference("network.proxy.type", 1)
    options.set_preference("network.proxy.socks", "127.0.0.1")
    options.set_preference("network.proxy.socks_port", 9150)
    options.set_preference("network.proxy.socks_remote_dns", False)

    # Inizializza il driver di Firefox con le opzioni configurate
    driver = webdriver.Firefox(options=options)

    # Apro il sito .onion
    driver.get(url)

    # Faccio uno screenshot e lo salvo
    driver.save_screenshot(f"{url}.png")

    # Chiudo il driver
    driver.quit()


if __name__ == "__main__":
    # Configuro il logger
    logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                        format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log

    # Parser per gli argomenti da linea di comando
    parser = argparse.ArgumentParser(
        description="Darkeb screenshot: estrae screenshot a partire dagli url dei siti .onion.")
    parser.add_argument(
        "--urls",
        nargs="*",  # Accetta zero o più argomenti
        help="Elenco degli url da cui estrarre gli screenshot (separati da spazio)."
    )
    args = parser.parse_args()

    if args.urls:
        for url in args.urls:
            logging.info(f"Esecuzione screenshot per l'url: {url}")
            save_screenshot(url)
    else:
        logging.error(
            "Nessun url specificato. Utilizzare l'argomento --urls per specificare gli url da cui estrarre gli screenshot.")

    # driver = configure_tor_driver()
    # take_screenshot("http://turkeyoetceface7wzxd7aep3iobnje7zjxnpticaincwzremhjwdgqd.onion/pt/meu-pedido1539.html?sl=1", driver=driver)
