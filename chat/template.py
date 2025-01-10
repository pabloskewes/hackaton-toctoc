import json
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_openai_response(prompt, template_data, model="gpt-3.5-turbo", max_tokens=150):
    """
    Get response from OpenAI API using template data
    """
    # API configuration
    api_key = os.getenv("OPENAI_API_KEY")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    # Create messages array using template
    messages = [
        {"role": "system", "content": template_data["content"]},
        {"role": "user", "content": prompt},
    ]

    # Add example conversations if present in template
    if "examples" in template_data:
        messages[1:1] = template_data["examples"]

    # Request payload
    data = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }

    # Make API request
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"].strip()
    else:
        raise Exception(f"API error: {response.status_code}\n{response.text}")


def load_template(template_name):
    """
    Load JSON template from templates directory
    """
    template_path = os.path.join(
        os.path.dirname(__file__), "..", "templates", template_name
    )
    with open(template_path, "r") as file:
        return json.load(file)


def main():
    try:
        # Load template first
        template_data = load_template("busqueda.json")
        print(template_data)
        # Example usage with template
        prompt = "quiero una casa en santiago centro, 3 habitaciones, 2 baños, 2 estacionamientos"
        response = get_openai_response(prompt, template_data)
        print("Respuesta de la API:", response)

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
