# Funcion para obtener la respuesta de OpenAI a partir de un prompt
import openai


def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
        max_tokens=400, # this is the maximum number of tokens that the model will generate
    )
    return response.choices[0].message["content"]