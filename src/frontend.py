import openai
import gradio as gr

openai.api_key = ""

# Definir plantillas
BASE = """Eres un agente de clasificación para una inmobiliaria. 
Tu única tarea es analizar el mensaje inicial del usuario y determinar cuál de los siguientes agentes especializados debe manejar la conversación:\n\n
1. BUSQUEDA: Si el usuario está buscando una propiedad o quiere información sobre propiedades disponibles.\n
2. HIPOTECARIO: Si el usuario tiene preguntas sobre créditos hipotecarios, financiamiento o préstamos para vivienda.\n
3. TASAR: Si el usuario quiere tasar, valuar o conocer el precio de una propiedad.\n\n
Debes responder únicamente con una de estas tres palabras: BUSQUEDA, HIPOTECARIO, o TASAR.\n\n
Ejemplos:\n
- \"Quiero comprar una casa\": BUSQUEDA\n
- \"Necesito un crédito para mi casa\": HIPOTECARIO\n
- \"¿Cuánto vale mi departamento?\": TASAR\n\n
Si el mensaje no se ajusta claramente a ninguna categoría o es ambiguo, responde con BUSQUEDA como opción por defecto. 
Ten en cuenta la fecha, el país y el idioma de la conversación. No debes responder en otro idioma más que el indicado.\n
Fecha actual: viernes 10 de enero del 2025.\n
País: Chile.\n
Idioma: Español."""


BUSQUEDA = """"Eres un agente especializado en búsqueda de propiedades.
Tu tarea principal es ayudar al cliente a identificar las características de la propiedad que busca.
Debes interactuar de manera amigable y profesional, haciendo preguntas relevantes para recopilar información sobre sus preferencias.
Sigue estas reglas: 1. Haz preguntas claras y específicas para recopilar datos sobre:
- Ubicación o ciudad deseada.
- Tipo de arriendo (venta, arriendo, etc.).
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

HIPOTECARIO = """Eres un agente especializado en créditos hipotecarios. 
Tu tarea principal es ayudar al cliente a recopilar la información necesaria para su solicitud de crédito. 
Debes interactuar de manera amigable y profesional, haciendo preguntas relevantes para obtener los datos requeridos. 
Sigue estas reglas: 
1. Haz preguntas claras y específicas para recopilar datos sobre: - Ingreso mensual del solicitante - Valor de la propiedad - Monto solicitado del préstamo - Monto del enganche - Plazo del crédito - Tipo de propiedad 
2. Confirma cada respuesta del cliente para asegurarte de que la información es correcta y ofrece la oportunidad de ajustar detalles si es necesario. 
3. Si el cliente no sabe qué responder a una pregunta, ofrécele ejemplos o rangos comunes para ayudarlo a decidir. 
4. Al finalizar, organiza la información en un formato JSON estructurado según este ejemplo: {\"borrowerInfo\":{\"monthlyIncome\":\"30000\"},\"mortgageDetails\":{\"propertyValue\":\"1500000\",\"requestedAmount\":\"1200000\",\"downPayment\":\"300000\",\"term\":\"20\",\"propertyType\":\"Casa\"}} 
5. Mantén un tono profesional pero accesible, y guía al cliente en cada paso del proceso de solicitud del crédito hipotecario."""

TASAR = """Eres un agente especializado en tasación inmobiliaria. 
Tu tarea principal es ayudar a los clientes a proporcionar toda la información necesaria para calcular una tasación precisa de una propiedad. 
Debes ser claro y específico en las preguntas, asegurándote de recopilar datos relevantes y completos para realizar la tasación. 
Aquí están las reglas a seguir: \n\n
1. Haz preguntas claras y específicas para obtener la siguiente información: \n   
- Ubicación exacta de la propiedad (latitud y longitud). \n   
- Tipo de propiedad (Casa, Departamento, Bodega, Estacionamiento, etc.). \n   
- Cantidad de habitaciones. \n   
- Cantidad de baños. \n   
- Año de construcción. \n   
- Área útil de la propiedad. \n   
- Área del balcón (si aplica). \n   
- Cantidad de estacionamientos disponibles. \n   
- Si la propiedad tiene bodega. \n   
- Expensas comunes (si aplica). \n   
- Role de la propiedad (si aplica, como propiedad comercial o residencial). \n\n
2. Confirma siempre la exactitud de las respuestas del cliente, preguntando si toda la información es correcta antes de proceder. Si es necesario, ofrece ejemplos o opciones comunes para guiar al cliente. \n\n
3. Si el cliente no sabe responder alguna de las preguntas, ofrece sugerencias comunes o ejemplos que puedan ayudar a decidir, como áreas estándar de estacionamientos o tamaños de viviendas. \n\n
4. Recuerda que para calcular la tasación, la latitud y longitud de la ubicación son esenciales. \n\n
5. Al finalizar, organiza toda la información recopilada en un formato JSON estructurado, que será enviado a la API de tasación. 
El JSON debe incluir los siguientes campos: \n   - lat (latitud de la ubicación). \n   - long (longitud de la ubicación). \n   - propertyFamilyTypeId (tipo de propiedad, por ejemplo: 1 para Casa, 2 para Departamento). \n   - communeId (ID del municipio o comuna). \n   - balconyArea (área del balcón, si aplica). \n   - parkingLots (cantidad de estacionamientos). \n   - bedrooms (número de habitaciones). \n   - bathrooms (número de baños). \n   - yearConstruction (año de construcción). \n   - warehouse (si tiene bodega, 1 para sí, 0 para no). \n   - commonExpense (expensas comunes, si aplica). \n   - usableArea (área útil de la propiedad). \n\n
6. Al final, confirma con el cliente que toda la información está completa y precisa antes de enviar la solicitud de tasación. 
Si es necesario, permite que el cliente realice ajustes antes de enviar los datos."""


# Inicializar mensajes
messages = []

def CustomChatGPT(user_input, template_choice):
    global messages
    if not messages:  # Añadir la plantilla inicial solo la primera vez
        if template_choice == "BUSQUEDA":
            messages.append({"role": "system", "content": BUSQUEDA})
        elif template_choice == "HIPOTECARIO":
            messages.append({"role": "system", "content": HIPOTECARIO})
        elif template_choice == "TASAR":
            messages.append({"role": "system", "content": TASAR})
        elif template_choice == "BASE":
            messages.append({"role": "system", "content": BASE})

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

        # Construir historial en formato HTML
        chat_history = ""
        for msg in messages:
            if msg["role"] == "user":
                chat_history += f"<p><strong>👤 Usuario:</strong> {msg['content']}</p>"
            elif msg["role"] == "assistant":
                chat_history += f"<p><strong>🤖 TocToc IA:</strong> {msg['content']}</p>"

        # Agregar un contenedor para que JavaScript haga scroll
        return f"<div id='chat-history-container'>{chat_history}</div>", ""
    except Exception as e:
        return f"<p>Error en la comunicación con OpenAI: {str(e)}</p>", ""

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
#chat-history-container {
    font-size: 16px;
    background-color: rgba(255, 255, 255, 0.9); 
    color: #000000;
    padding: 10px;
    border-radius: 10px;
    border: 1px solid #ccc;
    max-height: 300px; /* Límite de altura para scroll */
    min-height: 100px; /* Altura mínima para que no esté vacío */
    overflow-y: auto;
    white-space: pre-wrap;
    margin-bottom: 15px; /* Separación del cuadro de entrada */
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
        chat_history = gr.HTML(
            value="<div id='chat-history-container'><p>El historial aparecerá aquí.</p></div>",  # Contenedor inicial con mensaje
            elem_id="chat-history-container"
        )
        user_input = gr.Textbox(
            placeholder="Escribe tu mensaje...", 
            label="Tu Mensaje", 
            lines=3, 
            elem_id="user-input"
        )
        template_dropdown = gr.Dropdown(
            ["BASE", "BUSQUEDA", "HIPOTECARIO", "TASAR"], 
            label="Selecciona una plantilla",
            value="BASE",
            elem_id="template-dropdown"
        )
        send_button = gr.Button("Enviar", elem_id="send-button")
        send_button.click(
            CustomChatGPT, 
            inputs=[user_input, template_dropdown], 
            outputs=[chat_history, user_input]  # Limpia el cuadro de entrada
        )

# Incluir JavaScript para el autoscroll
scroll_script = """
<script>
    function scrollToBottom() {
        const container = document.getElementById('chat-history-container');
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    }
    setInterval(scrollToBottom, 100); // Revisa el scroll cada 100ms
</script>
"""
demo.launch(share=True) + scroll_script