import sqlite3
from sqlite3 import Binary

# Create tables
connection = sqlite3.connect("Speak.db", check_same_thread=False)
cursor = connection.cursor()
cursor.execute(
    """
    PRAGMA journal_mode=WAL;
    PRAGMA synchronous=NORMAL;
"""
)
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    );
"""
)
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS message (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        role TEXT,
        content BLOB,
        audio BLOB,
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


def insert_chat(name):
    with connection:
        cursor_ = connection.cursor()
        cursor_.execute("INSERT INTO chat (name) VALUES (?)", (name,))
        return cursor_.lastrowid


def insert_message(chat_id, role, content, audio):
    with connection:
        cursor_ = connection.cursor()
        cursor_.execute(
            "INSERT INTO message (chat_id, role, content, audio) VALUES (?, ?, ?, ?)",
            (chat_id, role, Binary(content), audio),
        )


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
