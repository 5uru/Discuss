import json
import logging
from backend.app.database import (
    get_chat_by_id,
    get_messages_by_chat_id,
    insert_message,
    insert_chat,
    get_all_chats,
)
from backend.app.llm_provider import generation
from backend.app.speech_to_text import transcribe
from backend.app.spell_check import grammar_coherence_correction, translate
from backend.app.text_to_speech import generate_audio

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

with open("tts_infos.json", "r") as f:
    language_info = json.load(f)


def message(chat_id, new_message_audio):
    logging.info(f"Processing message for chat_id: {chat_id}")
    chat_information = get_chat_by_id(chat_id)
    language = chat_information.language
    voice = chat_information.voice
    new_message_text = transcribe(new_message_audio, language)
    logging.info(f"Transcribed message: {new_message_text}")
    message_correction_data = grammar_coherence_correction(new_message_text, language)
    logging.info(f"Corrected message: {message_correction_data}")

    # Insert the new message
    insert_message(
        chat_id=chat_id,
        role="user",
        content=message_correction_data,
        audio=new_message_audio,
    )
    logging.info("New user message inserted into the database")

    old_messages = get_messages_by_chat_id(chat_id)
    prompt, roles_json = chat_information.prompt, chat_information.roles
    roles = json.loads(roles_json)
    old_messages_text = "".join(
        f"<|start_header_id|>{roles[msg.role]}<|end_header_id|>{json.loads(msg.content)['rewritten']}<|eot_id|>"
        for msg in reversed(old_messages)
    )
    prompt_finally = f"{prompt}{old_messages_text}<|start_header_id|>{roles['assistant']}<|end_header_id|>"
    response = generation(prompt_finally)
    logging.info(f"Generated response: {response}")
    audio = generate_audio(
        text=response,
        language=language_info[language][voice]["language"],
        speaker=language_info[language][voice]["speaker_id"],
    )

    # Insert the assistant's response
    insert_message(
        chat_id=chat_id,
        role="assistant",
        content={"rewritten": response, "translate": translate(response)},
        audio=audio,
    )
    logging.info("Assistant's response inserted into the database")

    return {
        "message_corrected": message_correction_data,
        "response": {
            "text": response,
            "audio": audio,
        },
    }


def create_chat(name, prompt, roles, description, language, voice):
    logging.info(f"Creating new chat: {name}")
    return insert_chat(name, prompt, roles, description, language, voice)


def get_chats():
    logging.info("Retrieving all chats")
    all_chats = get_all_chats()
    chat_list = [
        {"id": chat.id, "name": chat.name, "description": chat.description}
        for chat in all_chats
    ]
    logging.info(f"Retrieved {len(chat_list)} chats")
    return chat_list
