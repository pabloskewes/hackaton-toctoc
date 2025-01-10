import json
from typing import Optional, Any

import requests
from pydantic import BaseModel
from openinference.semconv.trace import OpenInferenceSpanKindValues, SpanAttributes

from toctoc.tracing import TracerProvider

TRACER = TracerProvider.get_tracer("toctoc-test")


class ChatMessage(BaseModel):
    """
    Represents a single message in a chat conversation.

    Attributes:
        role (str): The role of the sender (e.g., "user", "system", "assistant").
        content (Optional[str]): The content of the message.
    """

    role: str
    content: Optional[str] = None


class FunctionSchema(BaseModel):
    """
    Represents a function definition for OpenAI API function calling.

    Attributes:
        name (str): The name of the function.
        description (str): A description of what the function does.
        parameters (dict): The parameters required by the function, following JSON schema.
    """

    name: str
    description: str
    parameters: dict[str, Any]


class FunctionCallOutput(BaseModel):
    """
    Represents the output of a function call from the OpenAI API.

    Attributes:
        function_name (str): The name of the function to call.
        arguments (dict): The arguments to pass to the function.
    """

    function_name: str
    arguments: dict


class OpenAIClient:
    """
    A client for interacting with OpenAI's API.

    Attributes:
        api_key (str): The API key for authenticating requests to OpenAI.
        api_url (str): The base URL for OpenAI's API.
        headers (dict): The headers for the API requests.
    """

    def __init__(self, api_key: str):
        """
        Initializes the OpenAIClient with the API key.

        Args:
            api_key (str): Your OpenAI API key.
        """
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _send_request(self, payload: dict) -> dict:
        """
        Sends an HTTP POST request to the OpenAI API.

        Args:
            payload (dict): The payload for the API request.

        Returns:
            dict: The response from the OpenAI API.

        Raises:
            Exception: If the API request fails.
        """
        response = requests.post(self.api_url, json=payload, headers=self.headers)
        if response.status_code != 200:
            raise Exception(
                f"API request failed with status code {response.status_code}: {response.text}"
            )
        return response.json()

    def function_call(
        self,
        model: str,
        messages: list[ChatMessage],
        functions: list[FunctionSchema],
        temperature: float = 1.0,
    ) -> FunctionCallOutput:
        """
        Performs a function call using the OpenAI API.

        Args:
            model (str): The model to use (e.g., "gpt-3.5-turbo-0613").
            messages (List[ChatMessage]): A list of messages in the
            conversation.
            functions (List[FunctionSchema]): A list of function definitions.
            temperature (float): The temperature parameter for the API.
            Defaults to 1.0.

        Returns:
            dict: The API response as a dictionary.
        """
        with TRACER.start_as_current_span("FunctionCall") as span:
            payload = {
                "model": model,
                "messages": [msg.model_dump() for msg in messages],
                "functions": [fn.model_dump() for fn in functions],
                "temperature": temperature,
            }

            span.set_attributes(
                {
                    SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.CHAIN.value,
                    SpanAttributes.LLM_FUNCTION_CALL: json.dumps(
                        payload.get("functions")
                    ),
                }
            )
            response = self._send_request(payload)
            function_call = (
                response.get("choices")[0].get("message").get("function_call")
            )
            output = FunctionCallOutput(
                function_name=function_call.get("name"),
                arguments=json.loads(function_call.get("arguments")),
            )
            span.set_attributes(
                {
                    SpanAttributes.OUTPUT_VALUE: json.dumps(output.dict()),
                    SpanAttributes.LLM_INVOCATION_PARAMETERS: json.dumps(
                        {
                            "model": model,
                            "temperature": temperature,
                        }
                    ),
                }
            )
            return output
