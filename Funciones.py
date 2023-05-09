import os
import pickle
import openai






## Datos
server_settings = {}

# Obtener la ruta del directorio actual
dir_path = os.path.dirname(os.path.realpath(__file__))

# Concatenar el nombre del archivo al final de la ruta
file_path = os.path.join(dir_path, 'server_settings.pickle')


# Funcion para obtener la respuesta de OpenAI a partir de un prompt
def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
        max_tokens=400, # this is the maximum number of tokens that the model will generate
    )
    return response.choices[0].message["content"]

def get_image(prompt):
    response = openai.Image.create(
    prompt=prompt,
    n=1,
    size="1024x1024"
)
    image_url = response['data'][0]['url']
    return image_url





# Carga los server settings, atrapando la excepcion en caso de que no exista el archivo
def load_server_settings():
    try:
        with open(file_path, 'rb') as f:
            global server_settings
            server_settings= pickle.load(f)
            f.close()
    except FileNotFoundError: 
        server_settings = {}
        with open(file_path, 'wb') as f:
            pickle.dump(server_settings, f)
            f.close()

def toggle_feature(server_id):

    # Si el servidor no esta en la lista de servidores, lo agrega
    if server_id not in server_settings:
        server_settings[server_id] = {}

    # Cambia el estado de la caracteristica
    server_settings[server_id]['feature_enabled'] = not server_settings[server_id].get('feature_enabled', False)

    # Guarda los cambios en el archivo
    with open(file_path, 'wb') as f:
        pickle.dump(server_settings, f)
        f.close()