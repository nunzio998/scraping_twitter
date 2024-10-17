"""
Questo script permette al bot di Discord di connettersi ad un server e un canale specifici
e recuperare i messaggi all'interno.\n
Il bot deve essere aggiunto al server e al canale e avere quindi i permessi corretti per poter
accedere ai messaggi.\n
Autore: Francesco Pinsone
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
    Funzione per connettersi al bot di Discord. Dopo aver effettuato la connessione al bot la funzione estrae i messaggi dal canale\n
    :return: None, causa limitazioni di utilizzo dei bot discord i dati estratti con questo script non vengono salvati su db
    """
    print(f'Bot connesso come {client.user}')
    guild = discord.utils.get(client.guilds, id=int(GUILD_ID))
    if guild is None:
        logging.warning(
            f"Non riesco a trovare il server con ID {GUILD_ID}. Assicurati che il bot sia aggiunto al server e abbia i permessi corretti.")
        exit(0)

    channel = discord.utils.get(guild.channels, id=int(CHANNEL_ID))
    if channel is None:
        logging.warning(
            f"Non riesco a trovare il canale con ID {CHANNEL_ID}. Assicurati che il bot abbia i permessi corretti.")
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
