import sqlite3
from config import DATABASE_NAME

conn = sqlite3.connect(DATABASE_NAME, check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (chat_id INTEGER PRIMARY KEY, username TEXT, language TEXT)''')
    conn.commit()

def get_user_language(chat_id):
    c.execute("SELECT language FROM users WHERE chat_id = ?", (chat_id,))
    result = c.fetchone()
    return result[0] if result else 'en'

def get_user_username(chat_id):
    c.execute("SELECT username FROM users WHERE chat_id = ?", (chat_id,))
    result = c.fetchone()
    return result[0] if result else None

def set_user_data(chat_id, username, language):
    c.execute("INSERT OR REPLACE INTO users (chat_id, username, language) VALUES (?, ?, ?)",
              (chat_id, username, language))
    conn.commit()

init_db()