import json
from typing import List

from openinference.semconv.trace import OpenInferenceSpanKindValues, SpanAttributes

from toctoc.openai_client import OpenAIClient, ChatMessage
from toctoc.tracing import TracerProvider


TRACER = TracerProvider.get_tracer("toctoc-test")


class Chatbot:
    def __init__(
        self,
        openai_client: OpenAIClient,
        system_template: str,
    ):
        """
        Initialize the chatbot with OpenAI API key and model.

        Args:
            openai_client (OpenAIClient): The OpenAI client to use for API requests
        """
        self._client = openai_client
        self.system_template = system_template

        self.conversation_history: list[ChatMessage] = [
            ChatMessage(role="system", content=self.system_template)
        ]

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the conversation history.

        Args:
            role (str): The role of the message sender ("user" or "assistant")
            content (str): The message content
        """
        self.conversation_history.append(
            ChatMessage(
                role=role,
                content=content,
            )
        )

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = self.conversation_history[:1]

    def get_history(self) -> List[ChatMessage]:
        """
        Get the conversation history.

        Returns:
            List[Dict[str, str]]: List of message dictionaries
        """
        return self.conversation_history

    def _run(self) -> dict:
        raise NotImplementedError

    def run(self) -> dict:
        with TRACER.start_as_current_span(self.__class__.__name__) as span:
            response = self._run()

            span.set_attributes(
                {
                    SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.AGENT.value,
                    SpanAttributes.INPUT_VALUE: response.get("input"),
                    SpanAttributes.OUTPUT_VALUE: response.get("output"),
                }
            )

            messages = self.get_history()
            for i, msg in enumerate(messages):
                span.set_attributes(
                    {
                        f"llm.input_messages.{i}.message.content": msg.content,
                        f"llm.input_messages.{i}.message.role": msg.role,
                    }
                )

            self.add_message("assistant", response)
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
    'El valor de "message" debe ser la respuesta, confirmación o la próxima pregunta, y "finished" indica si el cliente ha finalizado el proceso (true) o si aún hay datos por recopilar (false). '
    "3. Confirma cada respuesta del cliente para asegurarte de que la información es correcta, y ofrece la oportunidad de ajustar detalles si es necesario. "
    "4. Si el cliente no sabe qué responder a una pregunta, ofrécele ejemplos o categorías comunes para ayudarlo a decidir. "
    "5. Finaliza las preguntas cuando el cliente indique que no tiene más información que agregar, o si confirmas que todos los datos necesarios han sido recopilados. "
    "6. Responde **únicamente en JSON**. No agregues texto fuera de este formato. "
    "Ejemplo de interacción: "
    'Cliente: "Quiero una casa en la playa." '
    "Tu respuesta: "
    '{"message": "¿En qué ciudad o zona costera deseas buscar la casa?", "finished": false}. '
    "Mantén el enfoque en los intereses y necesidades del cliente. Siempre responde solo en JSON."
)


JSON_RESPONSE_PROMPT_TEMPLATE = (
    "Eres un agente especializado en organizar información de propiedades. "
    "Tu tarea es recibir las preferencias recopiladas por otro agente en formato de texto y devolverlas como un JSON estructurado. "
    "Ejemplo: "
    '{"ubicacion":"Ciudad X","tipo_de_propiedad":"Casa","habitaciones":3,"banos":2,'
    '"caracteristicas_adicionales":["jardín","piscina"],"rango_de_precio":"100,000 - 150,000 USD"} '
    "Procesa la información y devuelve únicamente el JSON."
)


class PropertySearchAssitant(Chatbot):
    def __init__(self, openai_client: OpenAIClient):
        super().__init__(openai_client, PREFERENCES_PROMPT_TEMPLATE)

        self._search_property_filters = {}

    def _run(self) -> dict:
        response = self._client.completion(
            model="gpt-4-turbo-preview",
            messages=self.get_history(),
        )
        parsed_response = json.loads(response.content)
        message = parsed_response.get("message")
        finished = parsed_response.get("finished")

        print(f"{type(message)=}, {type(finished)=}")
        self.add_message("assistant", message)

        assert isinstance(message, str), "The response message must be a string."
        assert isinstance(finished, bool), "The finished flag must be a boolean."

        last_user_message = next(
            (msg for msg in self.get_history()[::-1] if msg.role == "user"), None
        )
        print(f"{last_user_message=}")
        print(f"{type(last_user_message)=}")
        output = {"input": last_user_message.content, "output": message}

        if finished:
            print("Finished collecting property preferences.")
            # self.clear_history()
            self.add_message("system", JSON_RESPONSE_PROMPT_TEMPLATE)
            final_response = self._client.completion(
                model="gpt-4-turbo-preview",
                messages=self.get_history(),
            )
            output["output"] = final_response.content

        return output


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()
    openai_client = OpenAIClient(api_key=os.getenv("OPENAI_API_KEY"))

    chatbot = PropertySearchAssitant(openai_client)
    chatbot.add_message(
        "user", "Quiero una casa en Santiago con 3 habitaciones y 2 baños."
    )
    output = chatbot.run()
    print(output)
