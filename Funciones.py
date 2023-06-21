import os
import pickle
import openai
from pydub import AudioSegment


## Datos
server_settings = {}

# Obtener la ruta del directorio actual
dir_path = os.path.dirname(os.path.realpath(__file__))

# Concatenar el nombre del archivo de texto al final de la ruta
file_path = os.path.join(dir_path, "server_settings.pickle")

# Concatenar el nombre del archivo de audio al final de la ruta
audio_file_path = os.path.join(dir_path, "transcriptions", "voice_message.mp3")

# Get the absolute path to the audio file
abs_audio_file_path = os.path.join(audio_file_path)

AudioSegment.ffmpeg = "C:/Program Files/ffmpeg-6.0-full_build/binffmpeg.exe"


# Funcion para obtener la respuesta de OpenAI a partir de un prompt
def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # this is the degree of randomness of the model's output
        max_tokens=400,  # this is the maximum number of tokens that the model will generate
    )
    return response.choices[0].message["content"]


# Funcion para obtener una imagen generada por OpenAI a partir de un prompt
def get_image(prompt):
    response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
    image_url = response["data"][0]["url"]
    return image_url


def isVoiceMessage(message):
    attachment = message.attachments[0]
    file_extension = attachment.filename.split(".")[-1]
    if file_extension in ["ogg"]:
        return True


async def save_audio_file(message):
    for attachment in message.attachments:
        # Save the audio file to disk
        filename = attachment.filename
        filepath = f"transcriptions/voice-message.mp3"
        print("Saving audio file to:", filepath)
        with open(filepath, "wb") as f:
            await attachment.save(f)
            f.close()


def format_to_mp3():
    # Load the audio file
    audio_file = AudioSegment.from_file("transcriptions/voice-message.mp3")

    # Export the audio file in the MP3 format
    audio_file.export("transcriptions/voice-message.mp3", format="mp3")


# Funcion para transcribir audio a texto, utilizando el modelo "whisper-1" de OpenAI
def transcribe_audio():
    format_to_mp3()

    audio_file = open("transcriptions/voice-message.mp3", "rb")
    transcript = openai.Audio.transcribe(model="whisper-1", file=audio_file)
    return transcript.text


# Carga los server settings, atrapando la excepcion en caso de que no exista el archivo
def load_server_settings():
    try:
        with open(file_path, "rb") as f:
            global server_settings
            server_settings = pickle.load(f)
            f.close()
    except FileNotFoundError:
        server_settings = {}
        with open(file_path, "wb") as f:
            pickle.dump(server_settings, f)
            f.close()


def toggle_feature(server_id):
    # Si el servidor no esta en la lista de servidores, lo agrega
    if server_id not in server_settings:
        server_settings[server_id] = {}

    # Cambia el estado de la caracteristica
    server_settings[server_id]["feature_enabled"] = not server_settings[server_id].get(
        "feature_enabled", False
    )

    # Guarda los cambios en el archivo
    with open(file_path, "wb") as f:
        pickle.dump(server_settings, f)
        f.close()
