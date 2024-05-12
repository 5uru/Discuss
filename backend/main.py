from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.app.chat_engine import get_chats
from backend.app.chat_engine import insert_chat
from backend.app.chat_engine import message as process_message
from backend.app.chat_engine import get_chat_messages
from backend.app.database import delete_messages_by_chat_id
from backend.app.database import delete_chat


class Chat(BaseModel):
    name: str
    prompt: str
    roles: Dict[str, str]
    description: str
    language: str
    voice: str


class MessageInput(BaseModel):
    chat_id: int
    new_message_audio: str


app = FastAPI()


@app.get("/chats")
def all_chats():
    return get_chats()


@app.post("/chats")
def create_chat(chat: Chat):
    return insert_chat(
        chat.name,
        chat.prompt,
        chat.roles,
        chat.description,
        chat.language,
        chat.voice,
    )


@app.delete("/chats/{chat_id}")
def delete_chat_route(chat_id: int):
    try:
        delete_chat(chat_id)
        return {"message": "Chat deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/chats/{chat_id}/messages")
def chat_messages(chat_id: int):
    try:
        return get_chat_messages(chat_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.delete("/chats/{chat_id}/messages")
def delete_chat_messages(chat_id: int):
    try:
        delete_messages_by_chat_id(chat_id)
        return {"message": "Chat messages deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/message")
def create_message(message: MessageInput):
    try:
        return process_message(
            chat_id=message.chat_id,
            new_message_audio=message.new_message_audio,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
