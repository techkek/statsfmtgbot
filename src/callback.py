from flask import Flask, request, redirect
import requests
from config import (
    ENV,
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    SPOTIFY_REDIRECT_URI,
    TG_BOT_USERNAME,
    TG_BOT_BETA_USERNAME,
)
from database import set_spotify_token, get_user_language

app = Flask(__name__)

@app.route("/callback")
def spotify_callback():
    try:
        code = request.args.get("code")
        state = request.args.get("state")

        if not code or not state:
            print("Error: Missing code or state")
            return "Error: Missing code or state", 400

        try:
            chat_id = int(state)
        except ValueError:
            print("Error: Invalid state parameter")
            return "Error: Invalid state parameter", 400

        token_url = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": SPOTIFY_REDIRECT_URI,
            "client_id": SPOTIFY_CLIENT_ID,
            "client_secret": SPOTIFY_CLIENT_SECRET,
        }

        try:
            response = requests.post(token_url, data=data, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error during token request: {str(e)}")
            return "Error: Unable to connect to Spotify", 500

        token_info = response.json()
        set_spotify_token(chat_id, token_info)

        redirect_url = f"https://t.me/{TG_BOT_USERNAME if ENV == 'production' else TG_BOT_BETA_USERNAME}?start=spotify"
        return redirect(redirect_url)

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return "An unexpected error occurred", 500