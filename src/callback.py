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
from language import get_text

app = Flask(__name__)


@app.route("/callback")
def spotify_callback():
    code = request.args.get("code")
    state = request.args.get("state")

    if not code or not state:
        return "Error: Missing code or state", 400

    chat_id = int(state)
    lang = get_user_language(chat_id)

    token_url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }

    response = requests.post(token_url, data=data)

    if response.status_code == 200:
        token_info = response.json()
        set_spotify_token(chat_id, token_info)
        # return get_text(lang, "spotify_connected_success")
        # call t.me/statsfmtgbot with ?start=spotify
    if ENV == "production":
        return redirect("https://t.me/" + TG_BOT_USERNAME + "?start=spotify")
    else:
        return redirect("https://t.me/" + TG_BOT_BETA_USERNAME + "?start=spotify")