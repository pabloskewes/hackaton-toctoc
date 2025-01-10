import requests
import json
import os

# Define tu clave de API de OpenAI
api_key = os.getenv('OPENAI_API_KEY')

# Define el endpoint de la API
url = "https://api.openai.com/v1/chat/completions"

# Configura las cabeceras para la solicitud HTTP
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Configura el cuerpo de la solicitud (payload)
data = {
    "model": "gpt-3.5-turbo",  # O usa "gpt-4" si tienes acceso
    "messages": [
        {"role": "system", "content": "Eres un asistente útil."},
        {"role": "user", "content": "¿Cómo funciona la inteligencia artificial?"}
    ],
    "max_tokens": 150
}

# Realiza la solicitud POST a la API
response = requests.post(url, headers=headers, data=json.dumps(data))

# Verifica si la solicitud fue exitosa
if response.status_code == 200:
    response_data = response.json()
    respuesta = response_data['choices'][0]['message']['content'].strip()
    print("Respuesta de la API:", respuesta)
else:
    print(f"Error en la solicitud: {response.status_code}")
    print(response.text)
