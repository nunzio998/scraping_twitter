# Scraping Multicanale: Dark Web, Discord, Telegram e Twitter (X)
Questo documento ha lo scopo di introdurre al progetto e fornire un quadro generale di quelli che sono 
gli obiettivi e la struttura. 
Per accedere alla documentazione dettagliata del codice sorgente è possibile seguire il seguente link: 
[Documentazione](https://docs-tesi.netlify.app)

## Descrizione del Progetto

L’obiettivo principale è la progettazione e l’implementazione di un sistema modulare per lo scraping e l’analisi di contenuti provenienti da diverse piattaforme digitali, il tutto da integrare in un processo di threat intelligence (ovvero il processo di raccolta, analisi e interpretazione di dati per identificare potenziali minacce). Il framework è stato progettato per garantire una raccolta efficiente e strutturata dei dati, centralizzandoli in un database MongoDB. Questo approccio consente non solo di gestire grandi volumi di informazioni, ma anche di effettuare analisi avanzate, favorendo un’identificazione proattiva delle minacce e migliorando la capacità decisionale delle organizzazioni coinvolte.

La metodologia adottata si basa su tecniche di scraping avanzato, sfruttando librerie come Selenium per piattaforme web, Telethon per Telegram e strumenti specifici per le altre piattaforme target. Ogni componente del sistema è stato sviluppato con un’architettura modulare, per garantire flessibilità e scalabilità. I dati raccolti sono organizzati in modo da facilitare l’integrazione con ulteriori strumenti di analisi e visualizzazione, migliorando l’efficacia del monitoraggio.
## Struttura del Progetto

Il progetto è organizzato come segue:
```
project-root/
├── docs/                                     # Cartella che contiene la documentazione dettagliata del progetto
├── src/
│   ├── DarkWeb_scraping/                     # Script per scraping sul dark web
│   │   ├── utils/                            # Utility (connessione DB, accesso)
│   │   │   ├── __init__.py                   # Script per contrassegnare la directory come modulo
│   │   │   ├── mongo_utils.json              # file che contiene le credenziali per l'accesso al DB
│   │   │   ├── screenshot_collector.py       # Script per la cattura di screenshot su ahmia browser
│   │   │   └── utils.py                      # Script che contiene le funzioni utilizzate dagli altri script
│   │   ├── __init__.py                       # Script per contrassegnare la directory come modulo
│   │   ├── ahmia_browser_scraper.py          # Script per scraping
│   │   ├── ahmia_scraper_ai.py               # Script per scraping con LLM per il parsing dei dati
│   │   ├── db_to_csv.py                      # Script che esporta i dati dal DB in un file csv
│   │   ├── drop_data_collection.py           # Script che cancella i tutti i dati
│   │   ├── plot_andamento_cve.py             # Script che produce un grafico sull'andamento delle vulnerabilità negli anni
│   │   ├── Tor_connection_test.py            # Script che esegue in test sulla connessione al Tor service
│   │   └── tor_setup.sh                      # Script che consente di eseguire un setup del servizio Tor
│   │
│   ├── Discord_scraping/                     # Script per scraping su Discord
│   │   ├── driver/
│   │   │   └── geckodriver                   # Driver per Firefox 
│   │   ├── utils/                            # Utility (connessione DB, accesso)
│   │   │   ├── __init__.py                   # Script per contrassegnare la directory come modulo
│   │   │   ├── conf.json                     # file che contiene i valori di configurazione dello script
│   │   │   ├── cookies.json                  # file dei cookies di una sessione Firefox in cui si è effettuato il login
│   │   │   ├── mongo_utils.json              # file che contiene le credenziali per l'accesso al DB
│   │   │   └── utils.py                      # Script che contiene le funzioni utilizzate dagli altri script
│   │   ├── __init__.py                       # Script per contrassegnare la directory come modulo         
│   │   ├── db_to_csv.py                      # Script che esporta i dati dal DB in un file csv
│   │   ├── discord_app_scraper.py            # Script che utilizza un bot per fare scraping su Discord
│   │   ├── discord_scraper_ai.py             # Script per scraping su Discord con LLM per il parsing dei dati
│   │   ├── discord_selenium_scraper.py       # Script per fare scraping su Discord
│   │   ├── drop_data_collection.py           # Script che cancella i tutti i dati
│   │   └── extract_cookies.py                # Script che consente di estrarre i cookies di sessione per superare i test captcha
│   │
│   ├── Telegram_scraping/                    # Script per scraping su Telegram
│   │   ├── utils/                            # Utility (connessione DB, accesso)
│   │   │   ├── __init__.py                   # Script per contrassegnare la directory come modulo
│   │   │   ├── conf.json                     # file che contiene i valori di configurazione dello script
│   │   │   ├── mongo_utils.json              # file che contiene le credenziali per l'accesso al DB
│   │   │   └── utils.py                      # Script che contiene le funzioni utilizzate dagli altri script 
│   │   ├── __init__.py                       # Script per contrassegnare la directory come modulo              
│   │   ├── db_to_csv.py                      # Script che esporta i dati dal DB in un file csv
│   │   ├── drop_data_collection.py           # Script che cancella i tutti i dati
│   │   └── telegram_scraper.py               # Script che esegue lo scraping su Telegram utilizzando la libreria Telethon
│   │
│   ├── X_scraping/                           # Script per scraping su Twitter (X)
│   │   ├── chrome/                           # Versione con Chrome
│   │   │   ├── deepfake_detection/           # directory relativa al task di deepfake detection
│   │   │   │   ├── utils/                    # Utility connessione API
│   │   │   │   │   └── credentials_api.json  # file che contiene le credenziali per l'accesso all'API
│   │   │   │   ├── __init__.py               # Script per contrassegnare la directory come modulo
│   │   │   │   └── deepfake_detection.py     # Script per il rilevamento di deepfake nei contenuti multimediali estrapolati
│   │   │   ├── utils/                        # Utility (connessione DB, accesso)
│   │   │   │   ├── __init__.py               # Script per contrassegnare la directory come modulo
│   │   │   │   ├── conf.json                 # file che contiene i valori di configurazione dello script
│   │   │   │   ├── mongo_utils.json          # file che contiene le credenziali per l'accesso al DB
│   │   │   │   └── utils.py                  # Script che contiene le funzioni utilizzate dagli altri script 
│   │   │   ├── __init__.py                   # Script per contrassegnare la directory come modulo
│   │   │   ├── beautifulsoup_analisys.py     # Script che contiene le funzioni per l'analisi dei dell'html raccolto
│   │   │   ├── db_to_csv.py                  # Script che esporta i dati dal DB in un file csv
│   │   │   ├── drop_data_collection.py       # Script che cancella i tutti i dati
│   │   │   ├── related_user_finder.py        # Script per la ricerca degli utenti correlati
│   │   │   ├── run_script.sh                 # Script per l'esecuzione dei singoli script
│   │   │   ├── tweet_scraper.py              # Script che esegue lo scraping dei tweet
│   │   │   └── user_info_scraper.py          # Script che esegue lo scraping delle informazioni degli utenti
│   │   ├── firefox/                          # Versione con Firefox
│   │   │   ├── deepfake_detection/           # directory relativa al task di deepfake detection
│   │   │   │   ├── utils/                    # Utility connessione API
│   │   │   │   │   └── credentials_api.json  # file che contiene le credenziali per l'accesso all'API
│   │   │   │   ├── __init__.py               # Script per contrassegnare la directory come modulo
│   │   │   │   └── deepfake_detection.py     # Script per il rilevamento di deepfake nei contenuti multimediali estrapolati
│   │   │   ├── driver/
│   │   │   │   └── geckodriver               # Driver per Firefox 
│   │   │   ├── utils/                        # Utility (connessione DB, accesso)
│   │   │   │   ├── __init__.py               # Script per contrassegnare la directory come modulo
│   │   │   │   ├── conf.json                 # file che contiene i valori di configurazione dello script
│   │   │   │   ├── mongo_utils.json          # file che contiene le credenziali per l'accesso al DB
│   │   │   │   └── utils.py                  # Script che contiene le funzioni utilizzate dagli altri script 
│   │   │   ├── __init__.py                   # Script per contrassegnare la directory come modulo
│   │   │   ├── beautifulsoup_analisys.py     # Script che contiene le funzioni per l'analisi dei dell'html raccolto
│   │   │   ├── db_to_csv.py                  # Script che esporta i dati dal DB in un file csv
│   │   │   ├── drop_data_collection.py       # Script che cancella i tutti i dati
│   │   │   ├── plot_andamento_cve.py         # Script che produce un grafico sull'andamento delle vulnerabilità negli anni
│   │   │   ├── related_user_finder.py        # Script per la ricerca degli utenti correlati
│   │   │   ├── run_script.sh                 # Script per l'esecuzione dei singoli script
│   │   │   ├── tweet_scraper.py              # Script che esegue lo scraping dei tweet
│   └── └── └── user_info_scraper.py          # Script che esegue lo scraping delle informazioni degli utenti
├── index.html
└── requirements.txt
```

---

## **Installazione e Setup**

### Prerequisiti
- **Python 3.8+**
- **MongoDB** installato e configurato
- Dipendenze presenti nel file `requirements.txt`

### Installazione delle Dipendenze

1. Clona questa repository:

   ```bash
   git clone https://github.com/tuo/repository.git
    ```
   
2. Installa le dipendenze:

   ```bash
   pip install -r requirements.txt
    ```
   
3. Inserimento delle credenziali:<br>
   All'interno della cartella 'utils' di ogni gruppo di script inserisci le tue credenziali di accesso alla piattaforma di riferimento e al database MongoDB.


---

## **Descrizione ed esecuzione degli script**

Spiega come eseguire gli script per ogni piattaforma. Puoi fornire esempi di esecuzione e spiegare eventuali parametri richiesti.


### Dark Web
Lo scraping sul Dark Web è stato implementato utilizzando il servizio Tor. Per eseguire lo scraping è necessario installare il servizio Tor e configurare il browser per utilizzarlo. Per gestire il servizio Tor è stato implementato 
lo script 'tor_setup.sh' che consente varie operazioni come l'istallazione, lo start/stop, il check della connessione e il riavvio del servizio.
Per eseguire lo script è quindi necessario il comando:
```bash
./tor_setup.sh
```
Dopo aver configurato il servizio Tor, è possibile eseguire lo scraping sul Dark Web:
- screenshot_collector.py: script per la cattura di screenshot su ahmia browser. Gli altri script possono utilizzare la funzione 'take_screenshot()' oppure si può eseguire lo script specificando degli url come argomento con il seguente comando:
  ```bash
    python src/DarkWeb_scraping/utils/screenshot_collector.py --urls <elenco di url separati da spazio>
    ```
- ahmia_browser_scraper.py: script che esegue lo scraping su Dark Web utilizzando il motore di ricerca Ahmia. Cerca per parole chiave e salva i risultati della ricerca per una futura analisi più apporofondita.
  ```bash
    python src/DarkWeb_scraping/ahmia_browser_scraper.py
    ```
- ahmia_scraper_ai.py: Script per scraping con LLM per il parsing dei dati.
  ```bash
    python src/DarkWeb_scraping/ahmia_scraper_ai.py
    ```
- db_to_csv.py: script che cancella tutti i dati presenti nel database.
    ```bash
        python src/DarkWeb_scraping/db_to_csv.py
   ```
- drop_data_collection.py: script che cancella tutti i dati presenti nel database.
    ```bash
        python src/DarkWeb_scraping/drop_data_collection.py
   ```
- Tor_connection_test.py: script che esegue un ulteriore test sulla connessione al servizio Tor.
    ```bash
        python src/DarkWeb_scraping/Tor_connection_test.py
    ```

### Discord
Lo scraping su Discord è stato implementato seguendo due modalità: tramite Selenium e tramite un bot.
- db_to_csv.py: script che cancella tutti i dati presenti nel database.
    ```bash
      python src/Discord_scraping/db_to_csv.py
    ```
- discord_app_scraper.py: script che esegue lo scraping su Discord utilizzando un bot. E' necessario che il bot faccia parte del server e del canale da cui si vogliono estrarre i dati.
    ```bash
      python src/Discord_scraping/discord_app_scraper.py
    ```
- discord_scraper_ai.py: script che esegue lo scraping su Discord utilizzando Selenium. E' necessario specificare il server e il canale da cui si vogliono estrarre i dati.
    ```bash
      python src/Discord_scraping/discord_scraper_ai.py
    ```
- discord_selenium_scraper.py: script che esegue lo scraping su Discord utilizzando Selenium. E' necessario specificare il server e il canale da cui si vogliono estrarre i dati.
    ```bash
      python src/Discord_scraping/discord_selenium_scraper.py
    ```
- drop_data_collection.py: script che cancella tutti i dati presenti nel database.
    ```bash
      python src/Discord_scraping/drop_data_collection.py
    ```
- extract_cookies.py: script che consente di estrarre i cookies di sessione per superare i test captcha.
    ```bash
      python src/Discord_scraping/extract_cookies.py
    ```

### Telegram
Lo scraping su Telegram è stato implementato utilizzando la libreria Telethon, che consente di interagire con l'API di Telegram.
- db_to_csv.py: script che cancella tutti i dati presenti nel database.
    ```bash
      python src/Telegram_scraping/db_to_csv.py
    ```
- telegram_scraper.py: script che esegue lo scraping su Telegram. E' necessario specificare i canali da cui si vogliono estrarre i dati e anche delle keyword d'interesse per filtrare i messaggi.
    ```bash
      python src/Telegram_scraping/telegram_scraper.py
    ```
- drop_data_collection.py: script che cancella tutti i dati presenti nel database.
    ```bash
      python src/Telegram_scraping/drop_data_collection.py
    ```

### X
Lo scraping su X è stato implementato con l'uso della libreria selenium, che consente di automatizzare l'interazione con il browser ed estrarre l'html delle pagine web.
L'html viene poi analizzato con la libreria BeautifulSoup per estrarre i dati di interesse. Sono presenti due versioni, una compatibile con Chrome e una con Firefox.

- tweet_scraper.py: script che esegue lo scraping dei tweet. E' necessario specificare le proprie credenziali d'accesso a Twitter.
    ```bash
      python src/X_scraping/chrome/tweet_scraper.py
    ```
    ```bash
      python src/X_scraping/firefox/tweet_scraper.py
    ```
- user_info_scraper.py: script che esegue lo scraping delle informazioni degli utenti autori dei tweet che ho precedentemente raccolto. 

    ```bash
      python src/X_scraping/chrome/user_info_scraper.py
    ```
    ```bash
      python src/X_scraping/firefox/user_info_scraper.py
    ```
- related_user_finder.py: script che trova gli utenti correlati a quelli che ho già raccolto. 

    ```bash
      python src/X_scraping/chrome/related_user_finder.py
    ```
    ```bash
      python src/X_scraping/firefox/related_user_finder.py
    ```
- drop_data_collection.py: script che cancella tutti i dati presenti nel database.
    ```bash
      python src/X_scraping/chrome/drop_data_collection.py
    ```
    ```bash
      python src/X_scraping/firefox/drop_data_collection.py
    ```
- db_to_csv.py: script che esporta i dati dal database in un file csv.
    ```bash
      python src/X_scraping/chrome/db_to_csv.py
    ```
    ```bash
      python src/X_scraping/firefox/db_to_csv.py
    ```
## **Dettagli sul Database**

Il progetto utilizza **MongoDB** per memorizzare i dati raccolti da ogni piattaforma. Ogni piattaforma ha un database dedicato:

- **darkweb_scraping**
- **discord_scraping**
- **telegram_scraping**
- **twitter_scraping**

Ogni database contiene diverse collection per categorizzare i dati raccolti in base al tipo di contenuto o alla specifica query di scraping. 
Le funzioni di connessione e gestione del database si trovano in `utils.py` all'interno di ciascuna cartella.

### darkweb_scraping
Il database contiene le seguenti collection:
- **ahmia_results**: contiene i risultati delle ricerche effettuate su Ahmia. <br>
    La struttura dei documenti è la seguente:
    ```json
    {
        "title": "string",
        "link": "string",
        "snippet": "string",
        "search_keywords": "array"
    }
    ```
### discord_scraping
Il database contiene le seguenti collection:
- **collection relative ai gruppi di cui ho fatto scraping**: contengono i messaggi estratti dai canali di Discord. <br>
    La struttura dei documenti è la seguente:
    ```json
    {
        "author": "string",
        "date": "string",
        "content": "string",
        "channel_name": "string"
    }
    ```
- **discord_target**: contiene gli id dei server e dei canali target. <br>
    La struttura dei documenti è la seguente:
    ```json
    {
        "server_id": "string",
        "channel_id": "string"
    }
    ```
  
### telegram_scraping
Il database contiene le seguenti collection:
- **Una collection per ogni canale di cui ho fatto scraping**: contengono i messaggi estratti dai canali di Telegram. <br>
    La struttura dei documenti è la seguente:
    ```json
    {
        "id": "int",
        "peer_id": "object",
        "date": "datetime",
        "message": "string",
        "mentioned": "boolean",
        "post": "boolean",
        "from_id": "object",
        "saved_peer_id": "string",
        "fwd_from": "object",
        "reply_to": "object",
        "media": "object",
        "entities": "array",
        "views": "int",
        "forwards": "string",
        "replies": "object",
        "edit_date": "datetime",
        "post_author": "string",
        "reactions": "int",
        "sender_name": "string",
        "sender_username": "string"
    }
    ```
  
### twitter_scraping
Il database contiene le seguenti collection:
- **Una collection per ogni gruppo hacker target o singola keyword di ricerca**<br>
    La struttura dei documenti è la seguente:
    ```json
    {
        "username": "string",
        "tag_username": "string",
        "date": "string",
        "content": "string",
        "reshared": "array",
        "images": "array",
        "videos": "array",
        "commments": "string",
        "reposts": "string",
        "likes": "string",
        "views": "string",
        "url": "string"
    }
    ```
- **target_groups**: contiene i nomi dei gruppi hacker target. <br>
    La struttura dei documenti è la seguente:
    ```json
    {
        "name": "string"
    }
    ```
- **users_info**: contiene le informazioni degli utenti autori dei tweet. <br>
    La struttura dei documenti è la seguente:
    ```json
    {
        "username": "string",
        "verified": "boolean",
        "num_post": "string",
        "following": "string",
        "follower": "string",
        "job": "string",
        "location": "string",
        "subscription": "string",
        "birthdate": "string",
        "website": "string"
    }
    ```
- **last_update**: contiene l'informazione relativa all'ultima esecuzione del codice e quindi all'ultima ricerca effettuata. Tale informazione viene chiaramente aggiornata ad ogni esecuzione. <br>
    La struttura dei documenti è la seguente:
    ```json
    {
        "id": "string",
        "last_update": "string"
    }
    ```
  
## **Dipendenze**
Le principali dipendenze del progetto includono:

- `selenium` per l'automazione del browser
- `pymongo` per l'interazione con MongoDB
- `requests` per scraping basato su richieste HTTP (se applicabile)
- `webdriver-manager` per la gestione dei driver di Chrome e Firefox
- `telethon` per l'interazione con l'API di Telegram
- `bs4` per l'analisi dell'html con beautifulsoup
- `discord` per l'interazione con l'API di Discord

Per installare tutte le dipendenze, esegui:

```bash
pip install -r requirements.txt
```

## **Documentazione Dettagliata**
Aprendo il link che segue è possibile trovare la documentazione dettagliata del codice nella quale script e funzioni 
vengono esposti e trattati più nel dettaglio:
[Documentazione](https://docs-tesi.netlify.app)<br>

La documentazione del progetto è stata realizzata tramite l'uso del tool Sphinx. Per la generazione e l'aggiornamento il comando utilizzato è il seguente:<br>

```bash
sphinx-build -b html . _build 
```
<br>
Tale comando va chiaramente utilizzato nella cartella 'docs' del progetto.