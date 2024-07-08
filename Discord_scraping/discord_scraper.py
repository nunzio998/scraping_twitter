import discord
import asyncio

# Le tue credenziali del bot di Discord
TOKEN = ''
GUILD_ID = ''
CHANNEL_ID = ''

# Parole chiave da cercare nei messaggi
keywords = ['parola1', 'parola2', 'parola3']

# Crea il client
client = discord.Client(intents=discord.Intents.default())


@client.event
async def on_ready():
    print(f'Bot connesso come {client.user}')
    guild = discord.utils.get(client.guilds, id=int(GUILD_ID))
    channel = discord.utils.get(guild.channels, id=int(CHANNEL_ID))

    messages = await channel.history(limit=100).flatten()
    filtered_messages = [message for message in messages if
                         any(keyword.lower() in message.content.lower() for keyword in keywords)]

    for message in filtered_messages:
        print(f'{message.author}: {message.content}')


client.run(TOKEN)
