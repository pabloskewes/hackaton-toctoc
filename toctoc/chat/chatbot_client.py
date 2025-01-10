import json
import os
from typing import List
from dotenv import load_dotenv

from openinference.semconv.trace import OpenInferenceSpanKindValues, SpanAttributes
from toctoc.openai_client import OpenAIClient, ChatMessage
from toctoc.tracing import TracerProvider

# Initialize tracer
TRACER = TracerProvider.get_tracer("toctoc-test")


class Chatbot:
    def __init__(self, openai_client: OpenAIClient, system_template: str):
        """
        Initialize the chatbot with OpenAI API client and system template.

        Args:
            openai_client (OpenAIClient): The OpenAI client to use for API requests.
            system_template (str): The system template for guiding the conversation.
        """
        self._client = openai_client
        self.system_template = system_template
        self.conversation_history: List[ChatMessage] = [
            ChatMessage(role="system", content=self.system_template)
        ]

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        self.conversation_history.append(ChatMessage(role=role, content=content))

    def clear_history(self) -> None:
        """Clear the conversation history, keeping only the system template."""
        self.conversation_history = self.conversation_history[:1]

    def get_history(self) -> List[ChatMessage]:
        """Retrieve the conversation history."""
        return self.conversation_history

    def _run(self) -> dict:
        """Abstract method for running chatbot logic. Must be implemented by subclasses."""
        raise NotImplementedError

    def run(self) -> dict:
        """Run the chatbot with tracing and handle OpenAI responses."""
        with TRACER.start_as_current_span(self.__class__.__name__) as span:
            response = self._run()

            span.set_attributes(
                {
                    SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.AGENT.value,
                    SpanAttributes.INPUT_VALUE: response.get("input"),
                    SpanAttributes.OUTPUT_VALUE: response.get("output"),
                }
            )

            for i, msg in enumerate(self.get_history()):
                span.set_attributes(
                    {
                        f"llm.input_messages.{i}.message.content": msg.content,
                        f"llm.input_messages.{i}.message.role": msg.role,
                    }
                )

            # self.add_message("assistant", response)
        return response


PREFERENCES_PROMPT_TEMPLATE = (
    "Eres un agente especializado en búsqueda de propiedades. "
    "Tu tarea principal es ayudar al cliente a identificar las características de la propiedad que busca. "
    "Sigue estas reglas estrictamente: "
    "1. Haz preguntas claras y específicas para recopilar datos sobre: "
    "- Ubicación o ciudad deseada. "
    "- Tipo de propiedad (casa, departamento, terreno, etc.). "
    "- Cantidad de habitaciones. "
    "- Cantidad de baños. "
    "- Otras características deseadas (jardín, piscina, estacionamiento, etc.). "
    "- Rango de precio estimado. "
    "2. Después de cada pregunta o interacción, devuelve una respuesta en formato JSON con la estructura: "
    '{"message": "str", "finished": true/false}. '
    "3. Confirma cada respuesta y ajusta si es necesario. "
    "4. Si el cliente no sabe qué responder, ofrécele ejemplos. "
    "5. Finaliza cuando todos los datos estén recopilados. "
    "6. Responde **únicamente en JSON**. "
)

JSON_RESPONSE_PROMPT_TEMPLATE = (
    "Eres un agente especializado en organizar información de propiedades. "
    "Recibe las preferencias recopiladas por otro agente y devuélvelas como JSON estructurado. "
    "Ejemplo: "
    '{"ubicacion":"Ciudad X","tipo_de_propiedad":"Casa","habitaciones":3,"banos":2,'
    '"caracteristicas_adicionales":["jardín","piscina"],"rango_de_precio":"100,000 - 150,000 USD"} '
    "Procesa la información y devuelve únicamente el JSON."
)


class PropertySearchAssistant(Chatbot):
    def __init__(self, openai_client: OpenAIClient):
        super().__init__(openai_client, PREFERENCES_PROMPT_TEMPLATE)
        self._property_info = {}

    def _run(self) -> dict:
        response = self._client.completion(
            model="gpt-4-turbo-preview", messages=self.get_history()
        )
        parsed_response = json.loads(response.content)
        message = parsed_response.get("message")
        finished = parsed_response.get("finished")

        assert isinstance(message, str), "The response message must be a string."
        assert isinstance(finished, bool), "The finished flag must be a boolean."

        self.add_message("assistant", message)
        last_user_message = next(
            (msg for msg in self.get_history()[::-1] if msg.role == "user"), None
        )

        output = {"input": last_user_message.content, "output": parsed_response}

        if finished:
            self.add_message("system", JSON_RESPONSE_PROMPT_TEMPLATE)
            final_response = self._client.completion(
                model="gpt-4-turbo-preview", messages=self.get_history()
            )
            # output["output"] = final_response.content
            self._property_info = json.loads(final_response.content)

        return output


if __name__ == "__main__":
    load_dotenv()
    openai_client = OpenAIClient(api_key=os.getenv("OPENAI_API_KEY"))

    chatbot = PropertySearchAssistant(openai_client)

    while True:
        user_input = input("User: ")
        chatbot.add_message("user", user_input)
        response = chatbot.run()
        output = response["output"]
        print(f"Assistant: {output.get('message')}")
        if output.get("finished"):
            print("Property information collected:")
            print(json.dumps(chatbot._property_info, indent=2))
            break
