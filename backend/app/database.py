import json
import sqlite3

# Create tables
connection = sqlite3.connect("Discute.db", check_same_thread=False)
cursor = connection.cursor()
cursor.execute("PRAGMA journal_mode=WAL;")
cursor.execute("PRAGMA synchronous=NORMAL;")
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        prompt TEXT NOT NULL,
        roles TEXT NOT NULL,
        description TEXT NOT NULL, 
        language TEXT DEFAULT 'en',
        voice TEXT NOT NULL    
    );
"""
)
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS message (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        role TEXT,
        content TEXT,
        audio TEXT,
        date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (chat_id) REFERENCES chat(id)
    );
"""
)
connection.commit()


def get_all_chats():
    with connection:
        cursor_ = connection.cursor()
        cursor_.execute("SELECT * FROM chat")
        return cursor_.fetchall()


def insert_chat(name, prompt, roles, description, language, voice):
    roles_json = json.dumps(roles)
    with connection:
        cursor_ = connection.cursor()
        cursor_.execute(
            "INSERT INTO chat (name, prompt, roles, description, language, voice) VALUES (?, ?,?,?, ?,?)",
            (name, prompt, roles_json, description, language, voice),
        )
        return cursor_.lastrowid


def insert_message(chat_id, role, content, audio):
    audio_json = json.dumps(audio)
    content = json.dumps(content)
    with connection:
        cursor_ = connection.cursor()
        cursor_.execute(
            "INSERT INTO message (chat_id, role, content, audio) VALUES (?, ?, ?, ?)",
            (chat_id, role, content, audio_json),
        )


def get_chat_by_id(chat_id):
    with connection:
        cursor_ = connection.cursor()
        cursor_.execute("SELECT * FROM chat WHERE id = ?", (chat_id,))
        return cursor_.fetchone()


def get_messages_by_chat_id(chat_id):
    with connection:
        cursor_ = connection.cursor()
        cursor_.execute(
            "SELECT id, chat_id, role, content, audio, date FROM message WHERE chat_id = ? ORDER BY date DESC",
            (chat_id,),
        )
        return cursor_.fetchall()


def delete_messages_by_chat_id(chat_id):
    with connection:
        cursor_ = connection.cursor()
        cursor_.execute(
            "DELETE FROM message WHERE chat_id = ? AND role != 'system'", (chat_id,)
        )


def delete_chat(chat_id):
    with connection:
        cursor_ = connection.cursor()
        cursor_.execute("DELETE FROM chat WHERE id = ?", (chat_id,))
        cursor_.execute("DELETE FROM message WHERE chat_id = ?", (chat_id,))
