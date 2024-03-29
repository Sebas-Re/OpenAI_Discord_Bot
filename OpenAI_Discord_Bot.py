import os
import pickle
from typing import Literal
import discord
from discord import Activity, ActivityType, app_commands
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


processed_messages = set()

# Cuando el bot se conecta, cambia su nombre a 'Yggdrasil' y lo informa en consola
@bot.event
async def on_ready():
    await bot.user.edit(username="El Oráculo")
    print(f"Logged in as {bot.user}!")

    activity = Activity(type=ActivityType.playing, name="Con OpenAI")
    await bot.change_presence(activity=activity)

    #print("Printing models:"+str(openai.Model.list()))
    #print("Printing engines:"+str(openai.Engine.list()))
    
    Funciones.load_server_settings()
    Funciones.load_channel_ids()


# Cada vez que entra un mensaje al canal seleccionado, el bot lo procesa y responde
@bot.event
async def on_message(message):
    # Extrae el id del servidor
    server_id = message.guild.id

    # Si el servidor esta en la lista de servidores, el canal en la lista de canales, y la caracteristica esta habilitada, procesa el mensaje
    if (
        Funciones.validServer(server_id)
        and Funciones.featureEnabled(server_id)
        and Funciones.validChannel(message)
    ):
        if message.author == bot.user:
            return
        else:
            if message.attachments:
                if Funciones.isVoiceMessage(message):
                    await Funciones.save_audio_file(message)
                    # await message.reply('Audio recibido y guardado. Transcribiendo...')
                    response = Funciones.transcribe_audio()
                    await message.reply(
                        'Mensaje de voz transcripto: \n"' + response + '"'
                    )
                else:
                    await message.reply(
                        "No se reconoce el formato del archivo. Solo se aceptan mensajes de voz."
                    )
            elif isinstance(message.content, str):
                prompt = f"{message.content}"
                response = Funciones.get_completion(prompt)
                print("User [" + message.author.name + "] >> " + prompt)
                print("[OpenAI] >> " + response)
                await message.reply(response)


# Comando para probar que el bot esta encendido
@bot.tree.command()
@app_commands.describe()
async def ping(interaction: discord.Interaction):
    print("Command received")
    await interaction.response.send_message(f"Pong! {round(bot.latency * 1000)}ms")


# Comando para habilitar/deshabilitar la caracteristica de lectura de chat
@bot.tree.command()
@app_commands.describe()
async def leerchat(interaction: discord.Interaction):
    print("Command received")

    # Extrae el id del servidor
    server_id = interaction.guild_id

    # Cambia el estado de la caracteristica
    Funciones.toggle_feature(server_id)

    # Informa el estado de la caracteristica
    if Funciones.server_settings[server_id]["feature_enabled"]:
        await interaction.response.send_message("Caracteristica habilitada.")
    else:
        await interaction.response.send_message("Caracteristica deshabilitada.")


# Comando para consultar a OpenAI
@bot.tree.command()
@app_commands.describe(consulta="Consulta a realizar al bot")
async def consulta(interaction: discord.Interaction, consulta: str):
    await interaction.response.defer()

    response = Funciones.get_completion(consulta)
    print("User [" + interaction.user.name + "] >> " + consulta)
    print("[OpenAI] >> " + response)

    await interaction.edit_original_response(content=response)


# Comando para consultar a OpenAI
@bot.tree.command()
@app_commands.describe(prompt="Prompt para generar la imagen")
async def imagine(interaction: discord.Interaction, prompt: str):
    # Restrict the command to the bot owner, basicamente porque es caro y no quiero que se abuse (Ademas de que, seamos honestos, Midjourney es mejor)
    if interaction.user.id == Secreto.Owner_ID:
        await interaction.response.defer()

        response = Funciones.get_image(prompt)
        print("User [" + interaction.user.name + "] >> " + prompt)
        print("[OpenAI] >> " + response)
        await interaction.edit_original_response(content=response)
    else:
        await interaction.response.send_message(
            "No tienes permiso para usar este comando."
        )


# Command for adding/removing a channel to the list of channels to read. The command should include an argument so the user can select whether to add or remove the channel.
@bot.tree.command()
@app_commands.describe(
    action="Agregar o remover un canal de la lista de canales a leer"
)
async def canal(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    action: Literal["Añadir", "Eliminar"],
):
    # If the selected action is to add a channel, add it to the list of channels to read using the añadir_canal function.
    if action == "Añadir":
        Funciones.add_channel(channel.id)
        await interaction.response.send_message(f"Canal {channel.mention} agregado.")
    # If the selected action is to remove a channel, remove it from the list of channels to read using the remover_canal function.
    elif action == "Eliminar":
        Funciones.remove_channel(channel.id)
        await interaction.response.send_message(f"Canal {channel.mention} removido.")


# Command for selecting between GPT 3 and 4. The command should include an argument so the user can select which model to use. The default should be GPT 3. Command is restricted to the bot owner.
@bot.tree.command()
@app_commands.describe(
    action="Seleccionar entre GPT 3, 4 y 4 Vision"
)
async def gpt(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    action: Literal["3", "4", "4 Vision"],
):

    # Checks if the user is the bot owner.
    if interaction.user.id == Secreto.Owner_ID:
        # If the selected action is "3" (GPT 3), set the model to GPT 3.
        if action == "3":
            Funciones.set_model("3")
            await interaction.response.send_message(f"Modelo seleccionado: GPT 3.")
        
        # If the selected action is "4" (GPT 4), set the model to GPT 4.
        elif action == "4":
            Funciones.set_model("4")
            await interaction.response.send_message(f"Modelo seleccionado: GPT 4.")
        
        # If the selected action is "4 Vision" (GPT 4 Vision), set the model to GPT 4 Vision.
        elif action == "4 Vision":
            Funciones.set_model("4 Vision")
            await interaction.response.send_message(f"Modelo seleccionado: GPT 4 Vision.")
    else:
        await interaction.response.send_message(
            "No tienes permiso para usar este comando."
        )


@bot.tree.command()
@app_commands.describe(
    idioma="Traduce el mensaje respondido al idioma seleccionado"
)
async def traducir(
    interaction: discord.Interaction,
    idioma: str,
    
    
):
# Si el mensaje seleccionado es de voz, lo descarga y lo transcribe
    ##este está mal y debe ser editado vvvvvvvvvv
    if interaction.message is None or interaction.message.reference is None:
     await interaction.response.send_message("Error: interaction was not triggered by a message reply.")
     return
    
    msg_sel_id = interaction.message.reference.message_id
    mensajeSeleccionado = await interaction.channel.fetch_message(msg_sel_id)
    if Funciones.isVoiceMessage(mensajeSeleccionado):
        await Funciones.save_audio_file(mensajeSeleccionado)
        # await message.reply('Audio recibido y guardado. Transcribiendo...')
        transcription = Funciones.transcribe_audio()
        response = Funciones.get_translation(transcription, idioma)
        print("User [" + mensajeSeleccionado.author.name + "] >> " + prompt)
        print("[OpenAI] >> " + response)
        await interaction.edit_original_response(
            content='Mensaje de voz transcripto: \n"' + response + '"'
        )
    # Si el mensaje seleccionado es de texto, lo traduce
    elif isinstance(mensajeSeleccionado.content, str):
        prompt = f"{mensajeSeleccionado.content}"
        response = Funciones.get_translation(prompt, idioma)
        print("User [" + mensajeSeleccionado.author.name + "] >> " + prompt)
        print("[OpenAI] >> " + response)
        await interaction.edit_original_response(content=response)



"""
@bot.tree.command()
@app_commands.describe(mensajeSeleccionado="Responde al mensaje de texto o voz a traducir al ejecutar este comando")
async def traducir(interaction: discord.Interaction, mensajeSeleccionado: discord.MessageReference):
    await interaction.response.defer()
    mensajeSeleccionado = await interaction.message.channel.fetch_message(mensajeSeleccionado.message_id)
    # Si el mensaje seleccionado es de voz, lo descarga y lo transcribe
    if Funciones.isVoiceMessage(mensajeSeleccionado):
        await Funciones.save_audio_file(mensajeSeleccionado)
        # await message.reply('Audio recibido y guardado. Transcribiendo...')
        transcription = Funciones.transcribe_audio()
        response = Funciones.get_translation(transcription)
        print("User [" + mensajeSeleccionado.author.name + "] >> " + prompt)
        print("[OpenAI] >> " + response)
        await interaction.edit_original_response(
            content='Mensaje de voz transcripto: \n"' + response + '"'
        )
    # Si el mensaje seleccionado es de texto, lo traduce
    elif isinstance(mensajeSeleccionado.content, str):
        prompt = f"{mensajeSeleccionado.content}"
        response = Funciones.get_translation(prompt)
        print("User [" + mensajeSeleccionado.author.name + "] >> " + prompt)
        print("[OpenAI] >> " + response)
        await interaction.edit_original_response(content=response)
"""


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
