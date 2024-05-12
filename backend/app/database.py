import json
import os
from datetime import datetime

from sqlalchemy import and_
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Create the database engine
engine = create_engine(
    "sqlite:///Discute.db", connect_args={"check_same_thread": False}
)

# Create the base class for declarative models
Base = declarative_base()


# Define the Chat model
class Chat(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)
    roles = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    language = Column(String, default="en")
    voice = Column(String, nullable=False)
    messages = relationship("Message", backref="chat", lazy="dynamic")

    def __repr__(self):
        return f"Chat(id={self.id}, name='{self.name}')"


# Define the Message model
class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey("chat.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    audio = Column(Text, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Message(id={self.id}, role='{self.role}', content='{self.content[:20]}...')"


# Create the tables
Base.metadata.create_all(engine)

# Create a session factory
Session = sessionmaker(bind=engine)


def get_all_chats():
    session = Session()
    chats = session.query(Chat).all()
    session.close()
    return chats


def insert_chat(name, prompt, roles, description, language, voice):
    session = Session()
    roles_json = json.dumps(roles)
    chat = Chat(
        name=name,
        prompt=prompt,
        roles=roles_json,
        description=description,
        language=language,
        voice=voice,
    )
    session.add(chat)
    session.commit()
    chat_id = chat.id
    session.close()
    return chat_id


def insert_message(chat_id, role, content, audio):
    session = Session()
    content_json = json.dumps(content)
    message = Message(chat_id=chat_id, role=role, content=content_json, audio=audio)
    session.add(message)
    session.commit()
    session.close()


def get_chat_by_id(chat_id):
    session = Session()
    chat = session.query(Chat).get(chat_id)
    session.close()
    return chat


def get_messages_by_chat_id(chat_id):
    session = Session()
    messages = (
        session.query(Message)
        .filter_by(chat_id=chat_id)
        .order_by(Message.date.desc())
        .all()
    )
    session.close()
    return messages


def delete_messages_by_chat_id(chat_id):
    session = Session()
    if chat := session.query(Chat).get(chat_id):
        # delete all audio files in "data/audio"
        for message in chat.messages:
            if audio_path := message.audio:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
            session.delete(message)  # delete the message
        session.commit()
        session.delete(chat)  # delete the chat after all messages have been deleted
        session.commit()
    session.close()


def delete_chat(chat_id):
    delete_messages_by_chat_id(chat_id)
    session = Session()
    session.query(Chat).filter_by(id=chat_id).delete()
    session.commit()
