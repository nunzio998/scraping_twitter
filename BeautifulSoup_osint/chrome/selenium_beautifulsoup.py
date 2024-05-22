import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd


driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://twitter.com/")
input("Premi Enter dopo aver effettuato il login...")

# Estrai i cookie
cookies = driver.get_cookies()

# Converti i cookie in un dizionario
cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}

# Salva i cookie in un file JSON (facoltativo)
with open('../twitter_cookies.json', 'w') as file:
    json.dump(cookies_dict, file)

print("Cookies acquisiti e salvati in twitter_cookies.json..")

# Cerca un hashtag o una parola chiave
search_box = driver.find_element(By.CSS_SELECTOR, 'input[data-testid="SearchBox_Search_Input"]')
search_box.send_keys('python')
search_box.send_keys(Keys.RETURN)
search_box.submit()



# Aspetta che i risultati siano caricati
time.sleep(5)


tweets = driver.get()


# Estrai i risultati (esempio: testo dei tweet)
#tweets = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="tweet"]')

# Estrai il testo dei tweet
#tweet_texts = [tweet.text for tweet in tweets]

# Chiudi il driver
#driver.quit()

# Salva i tweet in un DataFrame e poi in un CSV
#df = pd.DataFrame(tweet_texts, columns=["TweetText"])
#df.to_csv('tweets.csv', index=False)

# Stampa i tweet
#print(df)