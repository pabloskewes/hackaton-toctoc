import openai
import gradio as gr

openai.api_key = ""

# Definir plantillas
BUSQUEDA = """"Eres un agente especializado en búsqueda de propiedades.
Tu tarea principal es ayudar al cliente a identificar las características de la propiedad que busca.
Debes interactuar de manera amigable y profesional, haciendo preguntas relevantes para recopilar información sobre sus preferencias.
Sigue estas reglas: 1. Haz preguntas claras y específicas para recopilar datos sobre:
- Ubicación o ciudad deseada.
- Tipo de propiedad (casa, departamento, terreno, etc.).
- Cantidad de habitaciones.
- Cantidad de baños.
- Otras características deseadas (jardín, piscina, estacionamiento, etc.). 
- Rango de precio estimado. 
2. Confirma cada respuesta del cliente para asegurarte de que la información es correcta y ofrece la oportunidad de ajustar detalles si es necesario. 
3. Si el cliente no sabe qué responder a una pregunta, ofrécele ejemplos o categorías comunes para ayudarlo a decidir. 
4. Finaliza las preguntas cuando el cliente indique que no tiene más información que agregar o si confirmas que todos los datos necesarios han sido recopilados. 
5. Al finalizar, organiza toda la información en un formato JSON estructurado y devuelve ese JSON como resultado. 
Ejemplo de JSON final: {\"ubicacion\":\"Ciudad X\",\"tipo_de_propiedad\":\"Casa\",\"habitaciones\":3,\"banos\":2,\"caracteristicas_adicionales\":[\"jardín\",\"piscina\"],\"rango_de_precio\":\"100,000 - 150,000 USD\"} 
En cada interacción, prioriza la claridad y guía al cliente hacia respuestas útiles. 
Si detectas información contradictoria o confusa, pregunta amablemente para clarificar. 
Mantén el enfoque en los intereses y necesidades del cliente."""

TEMPLATE2 = """HOLA"""
TEMPLATE3 = """HOLA2"""

# Inicializar mensajes
messages = []

def CustomChatGPT(user_input, template_choice):
    global messages
    # Selección de plantilla
    if not messages:  # Añadir la plantilla inicial solo la primera vez
        if template_choice == "Template 1":
            messages.append({"role": "system", "content": BUSQUEDA})
        elif template_choice == "Template 2":
            messages.append({"role": "system", "content": TEMPLATE2})
        elif template_choice == "Template 3":
            messages.append({"role": "system", "content": TEMPLATE3})

    # Añadir entrada del usuario
    messages.append({"role": "user", "content": user_input})

    # Llamar al modelo de OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        ChatGPT_reply = response["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": ChatGPT_reply})

        # Construir historial para mostrar
        chat_history = ""
        for msg in messages:
            if msg["role"] == "user":
                chat_history += f"👤 Usuario: {msg['content']}\n"
            elif msg["role"] == "assistant":
                chat_history += f"🤖 TocToc IA: {msg['content']}\n"
        return chat_history, ""  # Retorna el historial actualizado y limpia el cuadro de entrada
    except Exception as e:
        return f"Error en la comunicación con OpenAI: {str(e)}", ""

# CSS personalizado
css = """
body {
    background-color: #000000; /* Fondo negro */
    margin: 0;
    font-family: Arial, sans-serif;
    color: #FFFFFF; /* Texto blanco */
}

/* Encabezado */
#header {
    display: flex;
    align-items: center; 
    justify-content: flex-start; 
    background-color: #FFFFFF; /* Fondo blanco */
    padding: 10px;
    color: black;
}

#menu-logo {
    width: 80px;
    height: auto;
    margin-right: 15px;
}

/* Menú de barra */
#menu-bar {
    text-align: center;
    background-color: #003366; /* Azul oscuro */
    color: white;
    font-size: 20px;
    padding: 10px;
    margin: 0;
}

/* Contenedor del chatbot */
#chat-container {
    background-color: rgba(0, 51, 102, 0.9); 
    border-radius: 10px;
    padding: 20px;
    max-width: 600px;
    margin: auto;
    margin-top: 20px;
    color: #FFFFFF; 
}

/* Historial */
#chat-history {
    font-size: 16px;
    background-color: rgba(255, 255, 255, 0.9); 
    color: #000000;
    padding: 10px;
    border-radius: 10px;
    border: 1px solid #ccc;
    max-height: 300px; /* Límite de altura para scroll */
    overflow-y: auto;
    white-space: pre-wrap;
    margin-bottom: 15px; /* Separación del cuadro de entrada */
}

/* Cuadro de entrada */
#user-input, #template-dropdown {
    width: 100%;
    font-size: 18px;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
    margin-bottom: 15px;
}

/* Botón de enviar */
#send-button {
    font-size: 18px;
    padding: 10px 20px;
    background-color: #0056A1; 
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

#send-button:hover {
    background-color: #003366; 
}
"""

# Interfaz de Gradio
with gr.Blocks(css=css) as demo:
    # Encabezado
    with gr.Row(elem_id="header"):
        gr.Image("logoblanco.png", elem_id="menu-logo", show_label=False)

    # Menú
    gr.Markdown(
        "<div id='menu-bar'>Inicio | Servicios | Contacto | Ayuda</div>", elem_id="menu-bar"
    )

    # Contenedor principal
    with gr.Column(elem_id="chat-container"):
        chat_history = gr.Textbox(
            label="Historial del Chat", 
            interactive=False, 
            elem_id="chat-history",
            lines=10  # Para mostrar varias líneas
        )
        user_input = gr.Textbox(
            placeholder="Escribe tu mensaje...", 
            label="Tu Mensaje", 
            lines=3, 
            elem_id="user-input"
        )
        template_dropdown = gr.Dropdown(
            ["Template 1", "Template 2", "Template 3"], 
            label="Selecciona una plantilla",
            value="Template 1",
            elem_id="template-dropdown"
        )
        send_button = gr.Button("Enviar", elem_id="send-button")
        send_button.click(
            CustomChatGPT, 
            inputs=[user_input, template_dropdown], 
            outputs=[chat_history, user_input]  # Limpia el cuadro de entrada
        )

demo.launch(share=True)
