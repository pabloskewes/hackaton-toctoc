from chatbot_client import Chatbot
from template import load_template
import os
from dotenv import load_dotenv


def main():
    # Load environment variables
    load_dotenv()

    # Initialize chatbot with your API key
    api_key = os.getenv("OPENAI_API_KEY")
    chatbot = Chatbot(api_key)

    # Load a template for real estate queries
    template_data = load_template("busqueda.json")

    # Add the system message from template
    chatbot.add_message("system", template_data["content"])

    # Add example conversations if present
    if "examples" in template_data:
        for example in template_data["examples"]:
            chatbot.add_message(example["role"], example["content"])

    while True:
        # Get user input
        user_message = input("\nYou: ")

        # Exit condition
        if user_message.lower() in ["exit", "quit", "salir"]:
            break

        # Get response from chatbot
        response = chatbot.get_response(user_message)
        print(f"Assistant: {response}")

    # Print final conversation history
    print("\nConversation History:")
    for message in chatbot.get_history():
        print(f"{message['role']}: {message['content']}")


if __name__ == "__main__":
    main()
