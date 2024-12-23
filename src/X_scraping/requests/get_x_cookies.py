import json

from selenium import webdriver

driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://www.twitter.com/login")
input("Premi Enter dopo aver effettuato il login...")

# Estrai i cookie
cookies = driver.get_cookies()

# Converti i cookie in un dizionario
cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}

# Salva i cookie in un file JSON (facoltativo)
with open('../twitter_cookies.json', 'w') as file:
    json.dump(cookies_dict, file)

print("Cookies acquisiti e salvati in twitter_cookies.json..")

# Chiudi il driver
driver.quit()