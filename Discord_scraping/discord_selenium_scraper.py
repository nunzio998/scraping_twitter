import selenium as selenium
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.common.exceptions import NoSuchElementException
from utils import read_json, beautifulsoup_analisys, scroll_up

credentials = read_json("utils/credentials.json")

service = Service('driver/geckodriver')

# Inizializzo driver  Firefox
driver = webdriver.Firefox(service=service)
# driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

# Loggarsi manualmente su Twitter
driver.get('https://discord.com/login')

# Imposto un'attesa esplicita di massimo 60 secondi
wait_login = WebDriverWait(driver, 60)

search_input_login = wait_login.until(EC.visibility_of_element_located((By.ID, 'uid_7')))

time.sleep(1)

# Cerco i campi nei quali far inserire automaticamente le credenziali
try:
    email_field = driver.find_element(By.ID, 'uid_7')
    email_field.send_keys(credentials["email"])
    time.sleep(1)
except NoSuchElementException:
    print("Campo email non trovato..")

try:
    password_field = driver.find_element(By.ID, 'uid_9')
    password_field.send_keys(credentials["password"])
    password_field.send_keys(Keys.RETURN)
    time.sleep(1)
except NoSuchElementException:
    print("Campo password non trovato..")

server_id = credentials['server_id']  # Guild_id
channel_id = credentials['channel_id']  # Channel_id

# carico la pagina del server su cui voglio fare scraping
search_url = f'https://discord.com/channels/{server_id}/{channel_id}'
driver.get(search_url)

# Attendo caricamento pagina
wait_messages = WebDriverWait(driver, 120)

# Aspettare che un elemento indicativo del completo caricamento della pagina sia visibile
search_messages = wait_messages.until(EC.visibility_of_element_located((By.CLASS_NAME, 'panels_a4d4d9')))

# Numero di volte che vuoi scorrere verso l'alto
scroll_times = 10

# Lista per salvare tutti i messaggi
all_messages = beautifulsoup_analisys(driver, scroll_times)


# Salva i messaggi in un file
with open(f'data_results/messages.txt', 'w') as f:
    for msg in all_messages:
        f.write(f"{msg['author']}-{msg['date']}: {msg['content']}\n")

driver.quit()
