"""
Questo script consente di configurare un bot di Discord per connettersi a un server (guild) e a un canale specifici,
e analizzare i messaggi presenti nel canale. Il bot esegue un filtraggio dei messaggi basato su parole chiave e registra
quelli che corrispondono ai criteri specificati.

**Funzionalità principali**:\n
1. **Connessione al server e al canale**:\n
   Il bot utilizza un token di autenticazione (TOKEN) per accedere all'API di Discord e connettersi al server (identificato
   tramite `GUILD_ID`) e al canale (identificato tramite `CHANNEL_ID`). È necessario che il bot sia stato aggiunto al server
   con i permessi adeguati per leggere i messaggi.

2. **Recupero della cronologia dei messaggi**:\n
   Una volta connesso, il bot recupera gli ultimi 100 messaggi (configurabile) dal canale specificato, usando il metodo
   `channel.history`.

3. **Filtro per parole chiave**:\n
   I messaggi vengono filtrati confrontandoli con una lista di parole chiave (`keywords`). Vengono selezionati solo i messaggi
   che contengono almeno una parola chiave specificata, ignorando la distinzione tra maiuscole e minuscole.

4. **Logging dei messaggi filtrati**:\n
   I messaggi che soddisfano i criteri di filtraggio vengono registrati utilizzando la libreria `logging`, includendo
   dettagli come l'autore del messaggio e il suo contenuto.

**Requisiti**:\n
    - Il bot deve essere stato aggiunto al server Discord e deve avere i permessi necessari per leggere i messaggi nel canale.\n
    - La libreria `discord.py` deve essere installata.\n
    - Devono essere configurati correttamente i seguenti parametri:\n
        - **TOKEN**: Il token del bot fornito dal portale Discord Developer.\n
        - **GUILD_ID**: L’ID del server Discord (guild) in cui si trova il canale.\n
        - **CHANNEL_ID**: L’ID del canale Discord da cui si vogliono estrarre i messaggi.\n
        - **keywords**: Una lista di parole chiave da cercare nei messaggi.

**Limiti**:\n
    - Data la natura limitante dei bot discord i dati estratti con questo scriopt non vengono salvati a db ma vengono solo mostrati nei log.\n
    - Lo script è progettato per scopi di analisi e test e non per un utilizzo continuativo o automatizzato su larga scala.\n

**Autore**: Francesco Pinsone.
"""

import discord
import logging

# Configuro il logger
logging.basicConfig(level=logging.INFO,  # Imposto il livello minimo di log
                    format='%(asctime)s - %(levelname)s - %(message)s')  # Formato del log

# Le tue credenziali del bot di Discord
TOKEN = ''
GUILD_ID = '1260220890160042004'
CHANNEL_ID = '1260220890160042007'

# Parole chiave da cercare nei messaggi
keywords = ['ciao']

# Crea il client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    """
    Evento che viene attivato quando il bot si connette correttamente a Discord.

    **Funzionalità**:\n
    1. **Verifica della connessione**:\n
        - Stampa un messaggio di conferma nel terminale indicando che il bot è online e operativo.\n
        - Usa il nome utente del bot (`client.user`) per confermare l'identità con cui il bot si è connesso.\n

    2. **Ricerca del server e del canale**:\n
        - Il bot cerca il server specificato tramite il suo ID (`GUILD_ID`) utilizzando la funzione `discord.utils.get`.\n
        - Se il server non viene trovato, registra un messaggio di avviso e termina il programma.\n
        - Allo stesso modo, cerca il canale specificato tramite il suo ID (`CHANNEL_ID`) all'interno del server trovato.\n
        - Se il canale non viene trovato, registra un avviso e termina il programma.\n

    3. **Recupero della cronologia dei messaggi**:\n
        - Recupera gli ultimi 100 messaggi (configurabile) presenti nel canale tramite il metodo asincrono `channel.history`.\n
        - I messaggi vengono salvati in una lista chiamata `messages`.\n

    4. **Filtraggio dei messaggi**:\n
        - Confronta il contenuto di ciascun messaggio con una lista di parole chiave predefinite (`keywords`).\n
        - I messaggi che contengono almeno una delle parole chiave, ignorando maiuscole e minuscole, vengono salvati in una lista chiamata `filtered_messages`.\n

    5. **Logging dei messaggi filtrati**:\n
        - Per ogni messaggio filtrato, registra il nome dell'autore e il contenuto del messaggio utilizzando la libreria `logging`.\n

    **Logica degli errori**:\n
        - Se il server o il canale specificati non vengono trovati, il bot registra un messaggio di avviso e termina il programma per evitare ulteriori problemi.\n
        - L'implementazione di questo controllo garantisce che il bot non generi errori cercando di accedere a un canale non valido.\n

    **Nota**:\n
        - Il limite di 100 messaggi recuperati è configurabile modificando il parametro `limit` in `channel.history`.\n
        - I dati estratti vengono solo registrati nel log e non salvati in un database.\n

    :return: Nessun valore restituito.
    """
    print(f'Bot connesso come {client.user}')
    guild = discord.utils.get(client.guilds, id=int(GUILD_ID))
    if guild is None:
        logging.warning(
            f"Non riesco a trovare il server con ID {GUILD_ID}. Assicurati che il bot sia aggiunto al server e abbia i permessi corretti.")
        exit(0)

    channel = discord.utils.get(guild.channels, id=int(CHANNEL_ID))
    if channel is None:
        logging.warning(f"Non riesco a trovare il canale con ID {CHANNEL_ID}. Assicurati che il bot abbia i permessi corretti.")
        exit(0)

    messages = []
    async for message in channel.history(limit=100):
        messages.append(message)

    filtered_messages = [message for message in messages if
                         any(keyword.lower() in message.content.lower() for keyword in keywords)]

    for message in filtered_messages:
        logging.info(f'{message.author}: {message.content}')


if __name__ == "__main__":
    client.run(TOKEN)
