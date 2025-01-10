import requests
from typing import List, Dict


class Chatbot:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        Initialize the chatbot with OpenAI API key and model.

        Args:
            api_key (str): Your OpenAI API key
            model (str): The model to use (default: gpt-3.5-turbo)
        """
        self.api_key = api_key
        self.model = model
        self.conversation_history: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the conversation history.

        Args:
            role (str): The role of the message sender ("user" or "assistant")
            content (str): The message content
        """
        self.conversation_history.append({"role": role, "content": content})

    def get_response(self, message: str) -> str:
        """
        Get a response from the chatbot for the given message.

        Args:
            message (str): The user's message

        Returns:
            str: The chatbot's response
        """
        # Add user message to history
        self.add_message("user", message)

        try:
            # Make direct API request to OpenAI
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": self.model,
                "messages": self.conversation_history,
                "temperature": 0.7,
            }

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            )

            response.raise_for_status()  # Raise exception for bad status codes
            data = response.json()

            # Extract the response text
            bot_response = data["choices"][0]["message"]["content"]

            # Add bot response to history
            self.add_message("assistant", bot_response)

            return bot_response

        except Exception as e:
            return f"Error: {str(e)}"

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []

    def get_history(self) -> List[Dict[str, str]]:
        """
        Get the conversation history.

        Returns:
            List[Dict[str, str]]: List of message dictionaries
        """
        return self.conversation_history
