import json
from selenium import webdriver
import time
from bs4 import BeautifulSoup


driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://www.twitter.com/login")
input("Premi Enter dopo aver effettuato il login...")

# Estrai i cookie
cookies = driver.get_cookies()

# Converti i cookie in un dizionario
cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}

# Salva i cookie in un file JSON (facoltativo)
with open('data_results/cookies.json', 'w') as file:
    json.dump(cookies_dict, file)
    print("Cookies acquisiti e salvati in twitter_cookies.json..")

# Mando richiesta get con query nei parametri
#search_url = 'https://x.com/search?q=killnet&src=typed_query'
search_url = "https://x.com/search?f=top&q=Killnet%20lang%3Aen%20-filter%3Alinks%20-filter%3Areplies&src=typed_query"
driver.get(search_url)

# Attendo caricamento pagina
time.sleep(5)

html_content = driver.page_source
soup = BeautifulSoup(html_content, 'html.parser')

# Salvo la risposta in un file HTML
with open('data_results/response.html', 'w') as f:
    f.write(soup.prettify())

driver.quit()

