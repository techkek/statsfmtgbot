import requests
from datetime import datetime

from config import API_BASE_URL, USER_AGENT
import random
from collections import Counter

import sys
sys.stdout.reconfigure(encoding='utf-8')


def get_complex_recommendations(username, limit=5):
    all_tracks = get_all_items(username, "", "tracks")
    all_albums = get_all_items(username, "", "albums")

    artists = Counter()
    for track in all_tracks:
        for artist in track["track"]["artists"]:
            artists[artist["id"]] += 1

    genres = Counter()
    for album in all_albums:
        for genre in album["album"]["genres"]:
            genres[genre] += 1        
    
    similar_artists = find_similar_artists(artists)
    unheard_tracks = find_unheard_tracks(username, similar_artists)
    unheard_albums = find_unheard_albums(username, similar_artists)
    scored_tracks = score_recommendations(unheard_tracks, genres)
    scored_albums = score_recommendations(unheard_albums, genres, type="albums")
    recommended_tracks = select_diverse_recommendations(scored_tracks, limit)
    recommended_albums = select_diverse_recommendations(scored_albums, limit)
    return recommended_tracks, recommended_albums


def find_similar_artists(artists):
    similar_artists = set()
    artist_list = list(artists.keys())
    random_artists = random.sample(artist_list, min(30, len(artist_list)))
    top_artists = [artist for artist, _ in artists.most_common(20)]
    combined_artists = list(set(top_artists + random_artists))
    for artist_id in combined_artists:
        related = get_related_artists(artist_id)
        similar_artists.update(related)
    top_artists_set = set(dict(artists.most_common(250)).keys())
    return list(similar_artists - top_artists_set)


def get_related_artists(artist_id):
    base_url = f"{API_BASE_URL}/artists/{artist_id}/related"
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        artists = []
        for artist in data["items"]:
            artists.append(artist["id"])
        return random.sample(artists, min(5, len(artists)))
    except requests.exceptions.RequestException as e:
        print(f"Error getting related artists: {e}")
        return []


def get_artist_top_tracks(artist_id):
    base_url = f"{API_BASE_URL}/artists/{artist_id}/tracks"
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        data = response.json()["items"]
        filtered_data = [item for item in data if item["durationMs"] >= 60000]
        return filtered_data[:min(30, len(filtered_data))]
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return []


def find_unheard_tracks(username, artists):
    unheard = []
    for artist_id in random.sample(artists, 10):
        top_tracks = get_artist_top_tracks(artist_id)
        user_tracks = set(
            track["track"]["id"] for track in get_all_items(username, "", "tracks")
        )
        unheard.extend(
            [track for track in top_tracks if track["id"] not in user_tracks]
        )
    return unheard


def find_unheard_albums(username, artists):
    unheard = []
    for artist_id in random.sample(artists, 10):
        albums = get_artist_albums(artist_id)
        user_albums = set(
            album["album"]["id"] for album in get_all_items(username, "", "albums")
        )
        unheard.extend([album for album in albums if album["id"] not in user_albums and album["type"] == "album"])
    return unheard


def get_artist_albums(artist_id):
    base_url = f"{API_BASE_URL}/artists/{artist_id}/albums"
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["items"]
    except requests.exceptions.RequestException as e:
        print(f"Error getting artist albums: {e}")
        return []


def score_recommendations(items, user_genres, type="tracks"):
    scored_items = []
    total_genre_count = sum(user_genres.values())

    for item in items:
        score = 0
        if item is None:
            continue
        if(type == "tracks"):
            item_genres = get_album(item["albums"][0]["id"])["item"]["genres"]
        else:
            item_genres = item["genres"]
        for genre in item_genres:
            score += user_genres.get(genre, 0) / total_genre_count

        score += random.uniform(0, 0.2)

        scored_items.append((item, score))

    return sorted(scored_items, key=lambda x: x[1], reverse=True)


def select_diverse_recommendations(scored_items, limit):
    selected = []
    artists_selected = set()

    for item, _ in scored_items:
        artist_id = (
            item["artists"][0]["id"] if "artists" in item else item["artist"]["id"]
        )
        if artist_id not in artists_selected:
            selected.append(item)
            artists_selected.add(artist_id)

        if len(selected) == limit:
            break

    return selected


def get_all_items(username, period, item_type):
    base_url = f"{API_BASE_URL}/users/{username}/top/{item_type}"
    all_items = []
    offset = 0
    limit = 500

    while True:
        params = {"limit": limit, "offset": offset, "range": period}
        headers = {"User-Agent": USER_AGENT}

        try:
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            items = data["items"]
            if not items:
                break

            all_items.extend(items)
            if item_type == "genres":
                break
            offset += limit

        except requests.exceptions.RequestException as e:
            print(f"Error during request: {e}")
            break

    return all_items


def format_item_info(item, item_type, username):
    if item_type == "tracks":
        return {
            "position": item["position"],
            "title": item["track"]["name"],
            "artist": item["track"]["artists"][0]["name"],
            "album": (
                item["track"]["albums"][0]["name"] if item["track"]["albums"] else "N/A"
            ),
            "streams": item["streams"],
            "duration_ms": item["track"]["durationMs"],
            "total_listening_time_ms": item["playedMs"],
            "spotify_popularity": item["track"]["spotifyPopularity"],
            "stats_id": item["track"]["id"],
            "preview_url": item["track"]["spotifyPreview"]
            or item["track"]["appleMusicPreview"]
            or "N/A",
            "album_image": (
                item["track"]["albums"][0]["image"]
                if item["track"]["albums"]
                else "N/A"
            ),
        }
    elif item_type == "albums":
        return {
            "position": item["position"],
            "title": item["album"]["name"],
            "artist": (
                item["album"]["artists"][0]["name"]
                if item["album"]["artists"] and item["album"]["artists"][0]
                else getArtistName(username, item["album"]["id"])
            ),
            "streams": item["streams"],
            "stats_id": item["album"]["id"],
            "image": item["album"]["image"] if item["album"].get("image") else "N/A",
        }
    elif item_type == "artists":
        return {
            "position": item["position"],
            "name": item["artist"]["name"],
            "streams": item["streams"],
            "stats_id": item["artist"]["id"],
            "image": item["artist"] if item["artist"].get("image") else "N/A",
        }
    elif item_type == "genres":
        return {
            "position": item["position"],
            "name": item["genre"]["tag"],
            "streams": item["streams"],
        }


def getArtistName(username, album_id):
    items = getAlbumItems(username, album_id)
    artist_id = items[0]["artistIds"][0]
    base_url = f"{API_BASE_URL}/artists/{artist_id}"
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(base_url, headers=headers)
    return response.json()["item"]["name"]


def getAlbumItems(username, album_id):
    base_url = f"{API_BASE_URL}/users/{username}/streams/albums/{album_id}"
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        items = data["items"]
        return items
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")


def get_first_last_listen(username, item_type, item_id, first_or_last):
    base_url = f"{API_BASE_URL}/users/{username}/streams/{item_type}/{item_id}"
    headers = {"User-Agent": USER_AGENT}
    params = {"limit": 1, "order": "asc" if first_or_last == "first" else "desc"}
    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if data["items"]:
            return datetime.strptime(
                data["items"][0]["endTime"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ).strftime("%d/%m/%Y")
        return "N/A"
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return "N/A"


def get_total_listening_time(username, item_type, item_id):
    base_url = f"{API_BASE_URL}/users/{username}/streams/{item_type}/{item_id}"
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        total_ms = sum(item["playedMs"] for item in data["items"])
        return format_listening_time(total_ms)
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return "N/A"


def format_listening_time(ms):
    seconds = ms // 1000
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m {seconds}s"


def get_album(album_id):
    base_url = f"{API_BASE_URL}/albums/{album_id}"
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None
