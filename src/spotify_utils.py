import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI
from database import get_user_setting, set_spotify_token, get_spotify_token, set_user_setting

def get_spotify_auth_url(chat_id):
    sp_oauth = SpotifyOAuth(
        SPOTIFY_CLIENT_ID,
        SPOTIFY_CLIENT_SECRET,
        SPOTIFY_REDIRECT_URI,
        scope = "playlist-modify-public,playlist-modify-private",
        cache_handler=None,
        show_dialog=True,
        state=str(chat_id)
    )
    auth_url = sp_oauth.get_authorize_url()
    return auth_url

def handle_spotify_callback(code, chat_id):
    sp_oauth = SpotifyOAuth(
        SPOTIFY_CLIENT_ID,
        SPOTIFY_CLIENT_SECRET,
        SPOTIFY_REDIRECT_URI,
        scope = "playlist-modify-public,playlist-modify-private",
        cache_handler=None
    )
    token_info = sp_oauth.get_access_token(code)
    set_spotify_token(chat_id, token_info)
    return True

def get_spotify_client(chat_id):
    token_info = get_spotify_token(chat_id)
    if not token_info:
        return None
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    return sp

def add_track_to_playlist(chat_id, track_id):
    sp = get_spotify_client(chat_id)
    if not sp:
        return False

    user_info = sp.me()
    playlist_id = get_user_setting(chat_id, "spotify-playlist-id", None)
    if not playlist_id:
        playlist = sp.user_playlist_create(user_info['id'], "[t.me/StatsFMTGBot] Saved songs", public=False, description="Songs saved from StatsFM Telegram Bot (t.me/StatsFMTGBot)")
        playlist_id = playlist['id']
        set_user_setting(chat_id, "spotify-playlist-id", playlist_id)
    
    playlist_tracks = sp.playlist_tracks(playlist_id)
    for item in playlist_tracks['items']:
        if item['track']['id'] == track_id:
            return 'already_saved'

    sp.user_playlist_add_tracks(user_info['id'], playlist_id, [track_id])
    return True
