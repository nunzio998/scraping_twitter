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
    Funzione per connettersi al bot di Discord.
    :return:
    """
    print(f'Bot connesso come {client.user}')
    guild = discord.utils.get(client.guilds, id=int(GUILD_ID))
    if guild is None:
        logging.warning(f"Non riesco a trovare il server con ID {GUILD_ID}. Assicurati che il bot sia aggiunto al server e abbia i permessi corretti.")
        exit(0)

    channel = discord.utils.get(guild.channels, id=int(CHANNEL_ID))
    if channel is None:
        logging.warning(f"Non riesco a trovare il canale con ID {CHANNEL_ID}. Assicurati che il bot abbia i permessi corretti.")
        exit(0)

    messages = []
    async for message in channel.history(limit=100):
        messages.append(message)

    filtered_messages = [message for message in messages if any(keyword.lower() in message.content.lower() for keyword in keywords)]

    for message in filtered_messages:
        logging.info(f'{message.author}: {message.content}')

client.run(TOKEN)
