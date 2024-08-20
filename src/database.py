import sqlite3, json
from config import DATABASE_NAME, cipher_suite

conn = sqlite3.connect(DATABASE_NAME, check_same_thread=False)

def init_db():
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
             (chat_id INTEGER PRIMARY KEY, language TEXT, settings TEXT, spotify_token TEXT, spotify_playlist_id TEXT)''')
    # c.execute('''ALTER TABLE users ADD COLUMN spotify_playlist_id TEXT''')
    conn.commit()

def get_user_language(chat_id):
    with conn:
        c = conn.cursor()
        c.execute("SELECT language FROM users WHERE chat_id = ?", (chat_id,))
        result = c.fetchone()
        return result[0] if result else 'en'
    
def set_user_data(chat_id, username, language):
    with conn:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO users (chat_id, username, language) VALUES (?, ?, ?)",
                (chat_id, username, language))
        conn.commit()

def get_user(chat_id):
    with conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,))
        return None if not c.rowcount else c.fetchone()

def get_user_settings(chat_id):
    with conn:
        c = conn.cursor()
        c.execute("SELECT settings FROM users WHERE chat_id = ?", (chat_id,))
        result = c.fetchone()
        if result and result[0]:
            return json.loads(result[0])
        return {}

def set_user_setting(chat_id, setting_name, value):
    c = conn.cursor()
    settings = get_user_settings(chat_id)
    settings[setting_name] = value
    c.execute("UPDATE users SET settings = ? WHERE chat_id = ?", (json.dumps(settings), chat_id))
    conn.commit()

def get_user_setting(chat_id, setting_name, default_value):
    settings = get_user_settings(chat_id)
    return settings.get(setting_name, default_value)

def set_spotify_token(chat_id, token):
    with conn:
        c = conn.cursor()
        encrypted_token = cipher_suite.encrypt(json.dumps(token).encode())
        c.execute("UPDATE users SET spotify_token = ? WHERE chat_id = ?", (encrypted_token, chat_id))
        conn.commit()
        set_user_setting(chat_id, "spotify-connected", True)

def get_spotify_token(chat_id):
    with conn:
        c = conn.cursor()
        c.execute("SELECT spotify_token FROM users WHERE chat_id = ?", (chat_id,))
        result = c.fetchone()
        if result and result[0]:
            decrypted_token = cipher_suite.decrypt(result[0])
            return json.loads(decrypted_token)
        return None

def clear_spotify_token(chat_id):
    with conn:
        c = conn.cursor()
        c.execute("UPDATE users SET spotify_token = NULL WHERE chat_id = ?", (chat_id,))
        conn.commit()
        set_user_setting(chat_id, "spotify-connected", False)


init_db()