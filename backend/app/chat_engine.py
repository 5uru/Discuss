import json

from backend.app.database import (
    get_chat_by_id,
    get_messages_by_chat_id,
    insert_message,
    insert_chat,
    get_all_chats,
)
from backend.app.llm_provider import generation
from backend.app.speech_to_text import transcribe
from backend.app.spell_check import grammar_coherence_correction
from backend.app.text_to_speech import generate_audio

language_info = {
    "en": {
        "llm_model": "mlx-community/Meta-Llama-3-8B-Instruct-4bit",
        "tts_model": "parler-tts/parler_tts_mini_v0.1",
        "voices": {
            "female_1": "A female speaker with a slightly low-pitched voice delivers her words quite expressively, in a very confined sounding environment with clear audio quality."
        },
    }
}


def message(chat_id, new_message_audio):
    chat_information = get_chat_by_id(chat_id)
    language = chat_information[5]
    voice = chat_information[6]
    new_message_text = transcribe(new_message_audio, language)
    message_correction_data = grammar_coherence_correction(new_message_text, language)

    # Insert the new message
    insert_message(
        chat_id=chat_id,
        role="user",
        content=message_correction_data,
        audio=new_message_audio,
    )

    old_messages = get_messages_by_chat_id(chat_id)
    prompt, roles_json = chat_information[2], chat_information[3]
    roles = json.loads(roles_json)

    old_messages_text = "\n".join(
        f"{roles[ msg[ 2 ] ]}: {json.loads(msg[ 3 ])[ 'rewritten' ]}"
        for msg in reversed(old_messages)
    )

    prompt_finally = f"{prompt}\n{old_messages_text}:\n{roles[ 'assistant' ]}:\n"
    response = generation(
        prompt_finally, llm_model=language_info[language]["llm_model"]
    )
    audio = generate_audio(
        text=response,
        description=language_info[language]["voices"][voice],
        tts_models=language_info[language]["tts_model"],
    )

    # Insert the assistant's response
    insert_message(
        chat_id=chat_id, role="assistant", content={"rewritten": response}, audio=audio
    )

    return {
        "message_corrected": message_correction_data,
        "response": {
            "text": response,
            "audio": audio,
        },
    }


def create_chat(name, prompt, roles, description, language, voice):
    return insert_chat(name, prompt, roles, description, language, voice)


def get_chats():
    all_chats = get_all_chats()
    return [
        {"id": chat[0], "name": chat[1], "description": chat[4]}
        for chat in all_chats
    ]
