import contextlib
import json

import streamlit as st
from backend.chat_engine import chat
from backend.speech_to_text import transcribe
from backend.spell_check import grammar_coherence_correction
from backend.text_to_speech import generate_audio
from streamlit_mic_recorder import mic_recorder

from backend import database


def answers(audio_bytes, chat_identifier):
    """
    Answers the user's audio input by transcribing it, correcting grammar coherence, generating a response,
    and saving the messages in the database.

    Args:
        audio_bytes (bytes): The audio input from the user.
        chat_identifier: The identifier of the chat.

    Returns:
        None"""
    # save the audio on tmp_file.wave
    with open("tmp_file.wav", "wb") as file:
        file.write(audio_bytes)
    audio_transcribe = transcribe()
    message_corrected = grammar_coherence_correction(audio_transcribe)
    database.insert_message(
        chat_id=chat_id,
        role="user",
        content=message_corrected,
        audio=audio_bytes,
    )
    all_messages = database.get_messages_by_chat_id(chat_identifier)
    # inverse messages list
    all_messages = all_messages[::-1]
    clean_messages = []
    for msg in all_messages:
        msg_content = json.loads(msg[3])
        if msg[2] in ["system", "assistant"]:
            clean_messages.append(msg_content)
        elif msg[2] == "user":
            clean_messages.append({"role": "user", "content": msg_content["rewritten"]})
    response = chat(clean_messages)
    response_audio = generate_audio(response["content"])
    database.insert_message(
        chat_id=chat_identifier,
        role="assistant",
        content=response,
        audio=response_audio,
    )


st.set_page_config(
    page_title="Speak",
    page_icon="🧊",
    layout="wide",
)
st.title("Speak: A chatbot for language learning")
col1, col2 = st.columns([1, 4])
chat_id = None
with col1:
    with st.status("**Select a chat**"):
        chats = database.get_all_chats()
        names = [chat[1] for chat in chats]
        if names:
            selected_chat = st.selectbox("Select chat", names)
            chat_id = chats[names.index(selected_chat)][0]
    with st.status("**Create a new chat**"):
        name = st.text_input("Chat name", "")
        prompt = st.text_area("Chat Prompt", "", help="Write a prompt for the chatbot")

        if st.button("Create"):
            try:
                if name in names:
                    st.error("Chat already exists")
                else:
                    chat_id = database.insert_chat(name)
                    content = {
                        "role": "system",
                        "content": prompt,
                    }
                    database.insert_message(
                        chat_id=chat_id, role="system", content=content, audio="NULL"
                    )
                    st.success("Chat created")
            except NameError:
                chat_id = database.insert_chat(name)
                content = {
                    "role": "system",
                    "content": prompt,
                }
                database.insert_message(
                    chat_id=chat_id, role="system", content=content, audio="NULL"
                )
                st.success("Chat created")
    with st.status(" **Assistant Description**"):
        with contextlib.suppress(Exception):
            messages = database.get_messages_by_chat_id(chat_id)
            for message in messages:
                if message[2] == "system":
                    st.write(json.loads(message[3])["content"])
    with st.status(":red[**Delete**]"):
        # Delete all messages
        if st.button("Delete all messages", type="primary"):
            database.delete_messages_by_chat_id(chat_id)
            st.success("All messages deleted")
        # Delete  chats
        if st.button("Delete chat", type="primary"):
            database.delete_chat(chat_id)
            st.success("Chat deleted")
with col2:
    if chat_id:
        if selected_chat:
            st.write(f" **{selected_chat}**")
        st.write("Record your voice:")
        c1, c2 = st.columns([9, 10])
        with c1:
            if audio := mic_recorder(
                start_prompt="⏺️ Record", stop_prompt="⏹️Stop", key="recorder"
            ):
                st.audio(audio["bytes"])
                with c2:
                    if st.button("Send"):
                        answers(audio["bytes"], chat_id)

        messages = database.get_messages_by_chat_id(chat_id)
        for message in messages:
            role = message[2]
            content = json.loads(message[3])
            audio = message[4]
            if role == "system":
                continue
            st.write(f"{role.capitalize()}: ")
            st.audio(audio)
            if role == "user":
                score_color = (
                    ":green[Correction]"
                    if content["score"] >= 80
                    else ":red[Correction]"
                )
                with st.status(score_color):
                    st.write(
                        f"Score: {score_color.replace('Correction', str(content['score']))}"
                    )
                    st.write(f"Original: {content['original']}")
                    st.write(f"Suggestion: {content['rewritten']}")
                    st.write(f"Grammar corrected: {content['grammar_corrected']}")
                    st.write(f"Coherence corrected: {content['coherence_corrected']}")
            else:
                with st.status("Transcription"):
                    st.write(content["content"])

    else:
        st.write("Select a chat to continue")
