import os
import pickle
import discord
from discord import app_commands
import openai
from discord.ext import commands
import Secreto
import Funciones

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        await self.tree.sync()



bot = MyClient(intents=discord.Intents.all())


# Set up the OpenAI API key
openai.api_key = Secreto.OpenAI_API_KEY

# Set up the Discord bot client
channels = [258435872020627463, 449413264443441152, 1104014621200883722, 1104014832254070797]

processed_messages = set()



# Cuando el bot se conecta, cambia su nombre a 'Yggdrasil' y lo informa en consola
@bot.event
async def on_ready():

    await bot.user.edit(username='El Oráculo')
    print(f'Logged in as {bot.user}!')

    Funciones.load_server_settings()
    



# Cada vez que entra un mensaje al canal seleccionado, el bot lo procesa y responde
@bot.event
async def on_message(message):

    # Extrae el id del servidor
    server_id = message.guild.id

    # Si el servidor esta en la lista de servidores y la caracteristica esta habilitada, procesa el mensaje
    if server_id in Funciones.server_settings and Funciones.server_settings[server_id].get('feature_enabled', False):
        if message.author == bot.user:
            return
        else:
            prompt = f"{message.content}"
            response = Funciones.get_completion(prompt)
            print("User ["+message.author.name+"] >> "+prompt)
            print("[OpenAI] >> "+response)
            await message.reply(response)
    else:
        return



# Comando para probar que el bot esta vivo
@bot.tree.command()
@app_commands.describe()
async def ping(interaction: discord.Interaction):
    print('Command received')
    await interaction.response.send_message(f'Pong! {round(bot.latency * 1000)}ms')



# Comando para habilitar/deshabilitar la caracteristica de lectura de chat
@bot.tree.command()
@app_commands.describe()
async def leerchat(interaction: discord.Interaction):
    print('Command received')
    
    # Extrae el id del servidor
    server_id = interaction.guild_id

    # Cambia el estado de la caracteristica
    Funciones.toggle_feature(server_id)

    # Informa el estado de la caracteristica
    if Funciones.server_settings[server_id]['feature_enabled']:
        await interaction.response.send_message('Caracteristica habilitada.')
    else:
        await interaction.response.send_message('Caracteristica deshabilitada.')



# Comando para consultar a OpenAI 
@bot.tree.command()
@app_commands.describe(consulta='Consulta a realizar al bot')
async def consulta(interaction: discord.Interaction, consulta: str):

    await interaction.response.defer()

    response = Funciones.get_completion(consulta)
    print("User ["+interaction.user.name+"] >> "+consulta)
    print("[OpenAI] >> "+response)

    await interaction.edit_original_response(content=response)
    

# Comando para consultar a OpenAI 
@bot.tree.command()
@app_commands.describe(prompt='Prompt para generar la imagen')
async def imagine(interaction: discord.Interaction, prompt: str):

    await interaction.response.defer()

    response = Funciones.get_image(prompt)
    print("User ["+interaction.user.name+"] >> "+prompt)
    print("[OpenAI] >> "+response)

    await interaction.edit_original_response(content=response)


bot.run(Secreto.Bot_Token)



"""
text-ada-001
text-embedding-ada-002
text-similarity-ada-001
curie-instruct-beta
ada-code-search-code
gpt-3.5-turbo-0301
ada-similarity
"babbage"
"davinci"
"text-davinci-edit-001"
"babbage-code-search-code"
"text-similarity-babbage-001"
"code-davinci-edit-001"
"text-davinci-001"
text-search-davinci-query-001
curie-search-query
davinci-search-query
babbage-search-document
ada-search-document
text-search-curie-query-001
curie-similarity
curie
text-similarity-davinci-001
text-davinci-002
davinci-similarity
cushman:2020-05-03
ada:2020-05-03
"""
