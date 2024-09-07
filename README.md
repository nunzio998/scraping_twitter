# Scraping Multicanale: Dark Web, Discord, Telegram e Twitter (X)

## Descrizione del Progetto

Questo progetto si propone di effettuare scraping su diverse piattaforme (Dark Web, Discord, Telegram e X) per raccogliere e analizzare dati. Ogni gruppo di script si occupa di una piattaforma specifica, ed è supportato da funzioni di utilità che facilitano l'interazione con un database MongoDB dedicato.
L'obiettivo finale del progetto è che i dati vengano analizzati per l'identificazione di potenziali future minacce per TERNA.
Lo scraping su **Twitter (X)** supporta sia il browser **Chrome** che **Firefox**, mentre le altre piattaforme vengono trattate in modo univoco. Tutti i dati raccolti vengono salvati in un database MongoDB diviso per piattaforma e ulteriormente suddiviso in collection a seconda delle necessità.

## Struttura del Progetto

Il progetto è organizzato come segue:
```
project-root/
├── DarkWeb_scraping/                     # Script per scraping sul dark web
│   ├── utils/                            # Utility (connessione DB, accesso)
│   │   ├── credentials.json              # file che contiene le credenziali per l'accesso al DB
│   │   └── utils.py                      # Script che contiene le funzioni utilizzate dagli altri script
│   ├── ahmia_browser_scraper.py          # Script per scraping
│   ├── drop_data_collection.py           # Script che cancella i tutti i dati
│   ├── Tor_connection_test.py            # Script che esegue in test sulla connessione al Tor service
│   └── tor_setup.sh                      # Script che consente di eseguire un setup del servizio Tor
│
├── Discord_scraping/                     # Script per scraping su Discord
│   ├── driver/
│   │   └── geckodriver                   # Driver per Firefox 
│   ├── utils/                            # Utility (connessione DB, accesso)
│   │   ├── credentials.json              # file che contiene le credenziali per l'accesso al DB
│   │   └── utils.py                      # Script che contiene le funzioni utilizzate dagli altri script         
│   ├── discord_app_scraper.py            # Script che utilizza un bot per fare scraping su un preciso canale di un preciso server Discord
│   ├── discord_selenium_scraper.py       # Script per fare scraping su Discord tramite Selenium
│   └── drop_data_collection.py           # Script che cancella i tutti i dati
│
├── Telegram_scraping/                    # Script per scraping su Telegram
│   ├── utils/                            # Utility (connessione DB, accesso)
│   │   ├── credentials.json              # file che contiene le credenziali per l'accesso al DB
│   │   └── utils.py                      # Script che contiene le funzioni utilizzate dagli altri script 
│   ├── drop_data_collection.py           # Script che cancella i tutti i dati
│   └── telegram_scraper.py               # Script che esegue lo scraping su Telegram utilizzando la libreria Telethon
│
├── X_scraping/                           # Script per scraping su Twitter (X)
│   ├── chrome/                           # Versione con Chrome
│   │   ├── utils/                        # Utility (connessione DB, accesso)
│   │   │   ├── credentials.json          # file che contiene le credenziali per l'accesso al DB
│   │   │   └── utils.py                  # Script che contiene le funzioni utilizzate dagli altri script 
│   │   ├── beautifulsoup_analisys.py     # Script che contiene le funzioni per l'analisi dei dell'html raccolto
│   │   ├── db_to_csv.py                  # Script che esporta i dati dal DB in un file csv
│   │   ├── drop_data_collection.py       # Script che cancella i tutti i dati
│   │   ├── run_script.sh                 # Script per l'esecuzione dei singoli script
│   │   ├── tweet_scraper.py              # Script che esegue lo scraping dei tweet
│   │   └── user_info_scraper.py          # Script che esegue lo scraping delle informazioni degli utenti
│   ├── firefox/                          # Versione con Firefox
│   │   ├── driver/
│   │   │   └── geckodriver               # Driver per Firefox 
│   │   ├── utils/                        # Utility (connessione DB, accesso)
│   │   │   ├── credentials.json          # file che contiene le credenziali per l'accesso al DB
│   │   │   └── utils.py                  # Script che contiene le funzioni utilizzate dagli altri script 
│   │   ├── beautifulsoup_analisys.py     # Script che contiene le funzioni per l'analisi dei dell'html raccolto
│   │   ├── db_to_csv.py                  # Script che esporta i dati dal DB in un file csv
│   │   ├── drop_data_collection.py       # Script che cancella i tutti i dati
│   │   ├── run_script.sh                 # Script per l'esecuzione dei singoli script
│   │   ├── tweet_scraper.py              # Script che esegue lo scraping dei tweet
└── └── └── user_info_scraper.py          # Script che esegue lo scraping delle informazioni degli utenti
```

---

## **Installazione e Setup**

Fornisci istruzioni dettagliate su come configurare e installare il progetto. Dovresti includere informazioni su come configurare il database, installare le dipendenze, e qualsiasi altro prerequisito necessario.

### Prerequisiti
- **Python 3.8+**
- **MongoDB** installato e configurato

### Installazione delle Dipendenze

1. Clona questo repository:

   ```bash
   git clone https://github.com/tuo/repository.git