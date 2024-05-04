import json
import sqlite3

# Create a global database connection
connection = sqlite3.connect("Speak.db", check_same_thread=False)


def get_all_chats():
    """
    Retrieve all chats from the database.

    Returns:
        List[Tuple[int, str]]: A list of tuples representing the chat ID and name.

    """
    with connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );
        """
        )
        cursor.execute("SELECT * FROM chat")
        chats = cursor.fetchall()
    return chats


def insert_chat(name):
    """
    Insert a new chat into the database.

    Args:
        name (str): The name of the chat.

    Returns:
        int: The ID of the inserted chat.

    """
    with connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );
        """
        )
        cursor.execute("INSERT INTO chat (name) VALUES (?)", (name,))
        chat_id = cursor.lastrowid
    return chat_id


def insert_message(chat_id, role, content, audio):
    """
    Insert a new message into the database.

    Args:
        chat_id (int): The ID of the chat.
        role (str): The role of the message.
        content (dict): The content of the message.
        audio (bytes or ndarray): The audio data of the message.

    Returns:
        None

    """
    with connection:
        cursor = connection.cursor()
        content_json = json.dumps(content)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS message (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                role TEXT,
                content TEXT,
                audio BLOB,
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chat(id)
            );
        """
        )
        cursor.execute(
            "INSERT INTO message (chat_id, role, content, audio) VALUES (?, ?, ?, ?)",
            (chat_id, role, content_json, audio),
        )


def get_messages_by_chat_id(chat_id):
    """
    Retrieve all messages for a given chat ID from the database.

    Args:
        chat_id (int): The ID of the chat.

    Returns: List[Tuple[int, int, str, str, bytes, str]]: A list of tuples representing the message ID, chat ID,
    role, content, audio, and date.

    """
    with connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS message (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                role TEXT,
                content TEXT,
                audio BLOB,
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chat(id)
            );
        """
        )
        cursor.execute(
            "SELECT * FROM message WHERE chat_id = ? ORDER BY date DESC", (chat_id,)
        )
        messages = cursor.fetchall()
    return messages


# delete all messages in a chat  except system messages
def delete_messages_by_chat_id(chat_id):
    """
    Delete all messages in a chat except system messages.

    Args:
        chat_id (int): The ID of the chat.

    Returns:
        None

    """
    with connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS message (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                role TEXT,
                content TEXT,
                audio BLOB,
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chat(id)
            );
        """
        )
        cursor.execute(
            "DELETE FROM message WHERE chat_id = ? AND role != 'system'", (chat_id,)
        )


# delete a chat
def delete_chat(chat_id):
    """
    Delete a chat and all its associated messages from the database.

    Args:
        chat_id (int): The ID of the chat.

    Returns:
        None

    """
    with connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );
        """
        )
        cursor.execute("DELETE FROM chat WHERE id = ?", (chat_id,))
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS message (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                role TEXT,
                content TEXT,
                audio BLOB,
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chat(id)
            );
        """
        )
        cursor.execute("DELETE FROM message WHERE chat_id = ?", (chat_id,))
