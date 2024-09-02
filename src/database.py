import sqlite3
import json
from config import DATABASE_NAME, encrypt_message, decrypt_message

conn = None

def init_db():
    global conn
    try:
        conn = sqlite3.connect(DATABASE_NAME, check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                 (chat_id INTEGER PRIMARY KEY, language TEXT, settings TEXT, spotify_token TEXT, spotify_playlist_id TEXT)''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")

def get_user_language(chat_id):
    try:
        with conn:
            c = conn.cursor()
            c.execute("SELECT language FROM users WHERE chat_id = ?", (chat_id,))
            result = c.fetchone()
            return result[0] if result else 'en'
    except sqlite3.Error as e:
        print(f"Error getting user language: {e}")
        return 'en'

def set_user_data(chat_id, username, language):
    try:
        with conn:
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO users (chat_id, language, settings) VALUES (?, ?, ?)",
                    (chat_id, language, json.dumps({'username': username})))
    except sqlite3.Error as e:
        print(f"Error setting user data: {e}")

def get_user(chat_id):
    try:
        with conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,))
            return c.fetchone()
    except sqlite3.Error as e:
        print(f"Error getting user: {e}")
        return None

def get_user_settings(chat_id):
    try:
        with conn:
            c = conn.cursor()
            c.execute("SELECT settings FROM users WHERE chat_id = ?", (chat_id,))
            result = c.fetchone()
            if result and result[0]:
                return json.loads(result[0])
            return {}
    except (sqlite3.Error, json.JSONDecodeError) as e:
        print(f"Error getting user settings: {e}")
        return {}

def set_user_setting(chat_id, setting_name, value):
    try:
        with conn:
            c = conn.cursor()
            settings = get_user_settings(chat_id)
            settings[setting_name] = value
            c.execute("UPDATE users SET settings = ? WHERE chat_id = ?", (json.dumps(settings), chat_id))
    except sqlite3.Error as e:
        print(f"Error setting user setting: {e}")

def get_user_setting(chat_id, setting_name, default_value):
    settings = get_user_settings(chat_id)
    return settings.get(setting_name, default_value)

def set_spotify_token(chat_id, token):
    try:
        with conn:
            c = conn.cursor()
            encrypted_token = encrypt_message(json.dumps(token))
            if encrypted_token:
                c.execute("UPDATE users SET spotify_token = ? WHERE chat_id = ?", (encrypted_token, chat_id))
                set_user_setting(chat_id, "spotify-connected", True)
            else:
                print("Error encrypting Spotify token")
    except sqlite3.Error as e:
        print(f"Error setting Spotify token: {e}")

def get_spotify_token(chat_id):
    try:
        with conn:
            c = conn.cursor()
            c.execute("SELECT spotify_token FROM users WHERE chat_id = ?", (chat_id,))
            result = c.fetchone()
            if result and result[0]:
                decrypted_token = decrypt_message(result[0])
                if decrypted_token:
                    return json.loads(decrypted_token)
            return None
    except (sqlite3.Error, json.JSONDecodeError) as e:
        print(f"Error getting Spotify token: {e}")
        return None

def clear_spotify_token(chat_id):
    try:
        with conn:
            c = conn.cursor()
            c.execute("UPDATE users SET spotify_token = NULL WHERE chat_id = ?", (chat_id,))
            set_user_setting(chat_id, "spotify-connected", False)
    except sqlite3.Error as e:
        print(f"Error clearing Spotify token: {e}")

init_db()