import os
from cryptography.fernet import Fernet

# Bot settings
BOT_TOKEN = "<your bot token>"
DATABASE_NAME = "./storage/user_data.db"  # Path to the database file
API_BASE_URL = "https://api.stats.fm/api/v1"  # Stats.fm API base URL
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
GITHUB_REPO = "https://github.com/techkek/statsfmtgbot"  # Link to the GitHub repository

# Environment settings
ENV = "development"  # "production" or "development" or "debug"

# Spotify settings
SPOTIFY_CLIENT_ID = (
    "<your_client_id>"  # https://developer.spotify.com/dashboard/applications
)
SPOTIFY_CLIENT_SECRET = (
    "<your_client_secret>"  # https://developer.spotify.com/dashboard/applications
)
HOST = (
    "<your_host_url>"  # URL of the server where the bot is hosted for the redirect URI
)
PORT = 8888 # Port for the Flask server
HOST_LOCAL = "localhost"  # Localhost URL for beta testing
PORT_LOCAL = 8888  # Localhost port for beta testing

SPOTIFY_REDIRECT_URI = (
    'https://+' + (HOST if ENV == 'production' else HOST_LOCAL)+ "/callback"
)  # Redirect URI for the Spotify API, must be accessible from the internet if you are not hosting the bot locally

# Telegram Bot settings
TG_BOT_USERNAME = "statsfmtgbot" # Telegram Bot username
TG_BOT_BETA_USERNAME = "statsfmtgbetabot" # Telegram Bot beta username

# Encryption settings
KEY_FILE = "./storage/encryption_key.key"  # Path to the encryption key file
def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        if ENV == "development" or ENV == "debug":
            print(f"Generated new encryption key and saved to {KEY_FILE}")
    else:
        with open(KEY_FILE, "rb") as key_file:
            key = key_file.read()
    return key

ENCRYPTION_KEY = load_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

# Available settings in the menu
AVAILABLE_SETTINGS = {
    "username": {
        "type": "text",
        "default": "",
        "label": {"en": "stats.fm Username", "it": "Nome utente stats.fm"},
    },
    "auto-preview": {
        "type": "boolean",
        "default": False,
        "label": {"en": "Auto-preview", "it": "Anteprima automatica"},
    },
    "spotify-connected": {
        "type": "callback",
        "default": False,
        "label": {"en": "Spotify Connected", "it": "Spotify Connesso"},
    },
}
