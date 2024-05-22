from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import json
from bs4 import BeautifulSoup
from selenium.webdriver import FirefoxService
from webdriver_manager.firefox import GeckoDriverManager


fp = webdriver.FirefoxProfile()


fp.set_preference("browser.download.folderList",2)

fp.set_preference("javascript.enabled", True)

# Geckodriver
service = Service('driver/geckodriver')

# Inizializzo driver  Firefox
options = webdriver.FirefoxOptions()

# Opzioni driver (su browser con about:support)
#options.add_argument('--user-data-dir=/Users/francesco/Library/Application Support/Firefox/Profiles/i5qodkh1.default-release-1716024453688')# Questo utilizza il tuo profilo Firefox
#options.add_argument("javascript.enabled")

#driver = webdriver.Firefox(service=service, options=options)
driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

# Loggarsi manualmente su Twitter
driver.get('https://www.twitter.com/login')
input("Premi Enter dopo aver effettuato il login...")

# Mando richiesta get con query nei parametri
search_url = 'https://x.com/search?q=python&src=typed_query'
driver.get(search_url)

# Attendo caricamento pagina
time.sleep(5)

# Estraggo HTML pagina con BeautifulSoup e lo stampo
html_content = driver.page_source
soup = BeautifulSoup(html_content, 'html.parser')

print(soup.prettify())


# Scorri la pagina per caricare più tweet
for _ in range(5):
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    time.sleep(2)

# Estraggo tweet dall'html ricevuto in risposta
tweets = driver.find_elements(By.XPATH, '//div[@data-testid="tweet"]')

# Estrai il testo dei tweet
tweet_texts = [tweet.text for tweet in tweets]

# Stampa i tweet
for i, tweet_text in enumerate(tweet_texts):
    print(f"Tweet {i+1}: {tweet_text}\n")

with open('tweets.json', 'w') as f:
    json.dump(tweet_texts, f)

driver.quit()
