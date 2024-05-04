from typing import List, Dict

import ollama


def chat(message: List[Dict[str, str]]) -> Dict[str, str]:
    """
    Chat with the Ollama chatbot.

    Args: message (List[Dict[str, str]]): A list of messages in the conversation. Each message is represented as a
    dictionary with "role" and "content" keys.
    
    Returns:
        str: The response message from the chatbot.

    """
    response = ollama.chat(model="qwen:7b-chat", messages=message,)
    return response["message"]
