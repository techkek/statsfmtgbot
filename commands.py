import random
import re
import requests
from database import get_user_language, get_user_username, set_user_data
from language import get_text
from api_client import (
    get_all_items,
    format_item_info,
    get_first_last_listen,
    get_total_listening_time,
    get_complex_recommendations,
)
from utils import send_long_message
import traceback


def register_commands(bot):
    try:

        @bot.message_handler(commands=["start"])
        def send_welcome(message):
            lang = get_user_language(message.chat.id)
            bot.reply_to(message, get_text(lang, "welcome"))

        @bot.message_handler(commands=["username"])
        def set_username(message):
            lang = get_user_language(message.chat.id)
            try:
                username = message.text.split()[1]
                set_user_data(message.chat.id, username, lang)
                bot.reply_to(message, get_text(lang, "username_saved").format(username))
            except IndexError:
                bot.reply_to(message, get_text(lang, "provide_username"))

        @bot.message_handler(commands=["random_artist"])
        def send_random_artist(message):
            chat_id = message.chat.id
            lang = get_user_language(chat_id)
            username = get_user_username(chat_id)

            if not username:
                bot.reply_to(message, get_text(lang, "set_username_first"))
                return

            temp_message = bot.send_message(
                chat_id, get_text(lang, "generating_random_artist")
            )

            all_artists = get_all_items(username, "", "artists")

            if all_artists:
                random_artist = random.choice(all_artists)
                artist_info = format_item_info(random_artist, "artists", username)

                # TODO languages
                response = f"[{artist_info['name']}](https://stats.fm/artist/{artist_info['stats_id']})\n"
                response += f"Streams: {artist_info['streams']} - #{artist_info['position']} most played artist overall\n"
                response += f"First listen: {get_first_last_listen(username, 'artists', artist_info['stats_id'], 'first')}\n"
                response += f"Last listen: {get_first_last_listen(username, 'artists', artist_info['stats_id'], 'last')}\n"
                response += f"Total listening time: {get_total_listening_time(username, 'artists', artist_info['stats_id'])}\n"

                bot.delete_message(chat_id, temp_message.message_id)

                image = artist_info.get("image")

                if(isinstance(image, str)):
                    if image != "N/A":
                        bot.send_photo(
                            chat_id,
                            image,
                            caption=response,
                            parse_mode="Markdown",
                        )
                    else:
                        bot.send_message(chat_id, response, parse_mode="Markdown")
                elif image["image"] != "N/A":
                    bot.send_photo(
                        chat_id,
                        image["image"],
                        caption=response,
                        parse_mode="Markdown",
                    )
                else:
                    bot.send_message(chat_id, response, parse_mode="Markdown")
            else:
                bot.delete_message(chat_id, temp_message.message_id)
                bot.reply_to(message, get_text(lang, "no_artists_found"))

        @bot.message_handler(commands=["random_album"])
        def send_random_album(message):
            chat_id = message.chat.id
            lang = get_user_language(chat_id)
            username = get_user_username(chat_id)

            if not username:
                bot.reply_to(message, get_text(lang, "set_username_first"))
                return

            temp_message = bot.send_message(
                chat_id, get_text(lang, "generating_random_album")
            )

            all_albums = get_all_items(username, "", "albums")

            if all_albums:
                random_album = random.choice(all_albums)
                album_info = format_item_info(random_album, "albums", username)

                # TODO languages

                response = f"[{album_info['title']}](https://stats.fm/album/{album_info['stats_id']})\n"
                response += f"Artist: {album_info['artist']}\n"
                response += f"Streams: {album_info['streams']} - #{album_info['position']} most played album overall\n"
                response += f"First listen: {get_first_last_listen(username, 'albums', album_info['stats_id'], 'first')}\n"
                response += f"Last listen: {get_first_last_listen(username, 'albums', album_info['stats_id'], 'last')}\n"
                response += f"Total listening time: {get_total_listening_time(username, 'albums', album_info['stats_id'])}\n"

                bot.delete_message(chat_id, temp_message.message_id)

                if album_info["image"] != "N/A":
                    bot.send_photo(
                        chat_id,
                        album_info["image"],
                        caption=response,
                        parse_mode="Markdown",
                    )
                else:
                    bot.send_message(chat_id, response, parse_mode="Markdown")
            else:
                bot.delete_message(chat_id, temp_message.message_id)
                bot.reply_to(message, get_text(lang, "no_albums_found"))

        @bot.message_handler(commands=["random"])
        @bot.message_handler(func=lambda message: message.text.lower() == "random")
        def send_random_track(message):
            chat_id = message.chat.id
            lang = get_user_language(chat_id)
            username = get_user_username(chat_id)

            if not username:
                bot.reply_to(message, get_text(lang, "set_username_first"))
                return

            temp_message = bot.send_message(chat_id, get_text(lang, "generating_song"))

            all_tracks = get_all_items(username, "", "tracks")

            if all_tracks:
                random_track = random.choice(all_tracks)
                track_info = format_item_info(random_track, "tracks", username)

                # TODO languages

                response = f"[{track_info['title']}](https://stats.fm/track/{track_info['stats_id']})\n"
                response += f"**{track_info['artist']}**\n"
                response += f"Album: {track_info['album']}\n"
                response += f"Streams: {track_info['streams']} - #{track_info['position']} most played song overall\n"
                response += f"First listen: {get_first_last_listen(username, 'tracks', track_info['stats_id'], 'first')}\n"
                response += f"Last listen: {get_first_last_listen(username, 'tracks', track_info['stats_id'], 'last')}\n"
                response += f"Total listening time: {get_total_listening_time(username, 'tracks', track_info['stats_id'])}\n"

                bot.delete_message(chat_id, temp_message.message_id)

                if track_info["album_image"] != "N/A":
                    bot.send_photo(
                        chat_id,
                        track_info["album_image"],
                        caption=response,
                        parse_mode="Markdown",
                    )
                else:
                    bot.send_message(chat_id, response, parse_mode="Markdown")

                if track_info["preview_url"] != "N/A":
                    try:
                        audio_data = requests.get(track_info["preview_url"]).content
                        bot.send_audio(
                            chat_id,
                            audio_data,
                            title=track_info["title"],
                            performer=track_info["artist"],
                        )
                    except requests.exceptions.RequestException:
                        bot.reply_to(message, get_text(lang, "unable_to_download"))
            else:
                bot.delete_message(chat_id, temp_message.message_id)
                bot.reply_to(message, get_text(lang, "no_tracks_found"))

        @bot.message_handler(commands=["random_genre"])
        def send_random_genre(message):
            chat_id = message.chat.id
            lang = get_user_language(chat_id)
            username = get_user_username(chat_id)

            if not username:
                bot.reply_to(message, get_text(lang, "set_username_first"))
                return

            temp_message = bot.send_message(
                chat_id, get_text(lang, "generating_random_genre")
            )

            all_genres = get_all_items(username, "", "genres")

            if all_genres:
                random_genre = random.choice(all_genres)
                genre_info = format_item_info(random_genre, "genres", username)

                # TODO languages

                response = f"[{genre_info['name']}](https://stats.fm/genre/{genre_info['name']})\n"
                response += f"Position: #{genre_info['position']}\n"
                response += f"Streams: {genre_info['streams']}\n"

                bot.delete_message(chat_id, temp_message.message_id)
                bot.send_message(chat_id, response, parse_mode="Markdown")
            else:
                bot.delete_message(chat_id, temp_message.message_id)
                bot.reply_to(message, get_text(lang, "no_genres_found"))

        @bot.message_handler(commands=["language"])
        def set_language(message):
            try:
                lang_code = message.text.split()[1].lower()
                if lang_code in ["en", "it"]:
                    set_user_data(
                        message.chat.id, get_user_username(message.chat.id), lang_code
                    )
                    bot.reply_to(message, get_text(lang_code, "language_set"))
                else:
                    bot.reply_to(
                        message,
                        get_text(
                            get_user_language(message.chat.id), "invalid_language"
                        ),
                    )
            except IndexError:
                bot.reply_to(
                    message,
                    get_text(get_user_language(message.chat.id), "invalid_language"),
                )

        @bot.message_handler(commands=["help"])
        def send_help(message):
            lang = get_user_language(message.chat.id)
            bot.reply_to(message, get_text(lang, "help_message"))

        @bot.message_handler(
            func=lambda message: message.text.lower().startswith(
                ("/top", "/albums", "/artists", "/genres")
            )
        )
        def send_top_items(message):
            chat_id = message.chat.id
            lang = get_user_language(chat_id)
            username = get_user_username(chat_id)

            if not username:
                bot.reply_to(message, get_text(lang, "set_username_first"))
                return

            item_type = re.match(r"[a-zA-Z]+", message.text.lstrip("/")).group(0)

            command_parts = message.text.split(item_type)

            if len(command_parts) < 2:
                bot.reply_to(message, get_text(lang, "invalid_top_command"))
                return

            command = command_parts[1]

            number = ""
            for char in command:
                if char.isdigit():
                    number += char
                else:
                    break

            if not number or int(number) < 1 or int(number) > 250:
                bot.reply_to(message, get_text(lang, "invalid_top_command"))
                return

            period = command[len(number) :]
            if period not in ["m", "hy", "lt"]:
                bot.reply_to(message, get_text(lang, "invalid_top_command"))
                return

            period_map = {"m": "weeks", "hy": "months", "lt": "lifetime"}
            api_period = period_map[period]

            if item_type == "top":
                item_type = "tracks"
            temp_message = bot.send_message(
                chat_id, get_text(lang, "generating_top", get_text(lang, item_type))
            )

            all_items = get_all_items(username, api_period, item_type)[: int(number)]

            if all_items:
                response = f"Top {number} {get_text(lang, item_type)} {get_text(lang, period)}:\n\n"
                for item in all_items:
                    item_info = format_item_info(item, item_type, username)
                    if item_type == "tracks":
                        response += f"{item_info['position']}. [{item_info['title']}](https://stats.fm/track/{item_info['stats_id']}) - {item_info['artist']} ({item_info['streams']} {get_text(lang, 'streams')})\n"
                    elif item_type == "albums":
                        response += f"{item_info['position']}. [{item_info['title']}](https://stats.fm/{item_type[:-1]}/{item_info['stats_id']}) ({item_info['streams']} {get_text(lang, 'streams')})\n"
                    elif item_type == "artists":
                        response += f"{item_info['position']}. {item_info['name']} ({item_info['streams']} {get_text(lang, 'streams')})\n"
                    elif item_type == "genres":
                        response += f"{item_info['position']}. {item_info['name']} ({item_info['streams']} {get_text(lang, 'streams')})\n"
                    else:
                        response = "Invalid item type\n"
                        bot.delete_message(chat_id, temp_message.message_id)
                        bot.reply_to(message, response)
                        print(f"Invalid item type: {item_type}")
                        return
                bot.delete_message(chat_id, temp_message.message_id)
                send_long_message(bot, chat_id, response, parse_mode="Markdown")
            else:
                bot.delete_message(chat_id, temp_message.message_id)
                bot.reply_to(message, get_text(lang, "no_items_found"))

        @bot.message_handler(commands=["recommend"])
        def send_recommendations(message):
            chat_id = message.chat.id
            lang = get_user_language(chat_id)
            username = get_user_username(chat_id)

            if not username:
                bot.reply_to(message, get_text(lang, "set_username_first"))
                return

            temp_message = bot.send_message(
                chat_id, get_text(lang, "generating_recommendations")
            )

            try:
                recommended_tracks, recommended_albums = get_complex_recommendations(
                    username
                )

                response = f"{get_text(lang, 'recommended_tracks')}:\n\n"
                for i, track in enumerate(recommended_tracks, 1):
                    response += f"{i}.[{track['name']}](https://stats.fm/track/{track['id']}) - [{track['artists'][0]['name']}](https://stats.fm/artist/{track['artists'][0]['id']})\n"

                response += f"\n{get_text(lang, 'recommended_albums')}:\n\n"
                for i, album in enumerate(recommended_albums, 1):
                    response += f"{i}.[{album['name']}](https://stats.fm/album/{album['id']}) - [{album['artists'][0]['name']}](https://stats.fm/artist/{album['artists'][0]['id']})\n"

                bot.delete_message(chat_id, temp_message.message_id)
                send_long_message(bot, chat_id, response, parse_mode="Markdown")
            except Exception as e:
                bot.delete_message(chat_id, temp_message.message_id)
                bot.reply_to(message, get_text(lang, "error_recommendations"))
                print(f"Error getting recommendations: {e} - {traceback.format_exc()}")

    except Exception as e:
        print(f"Error registering commands: {e} - {traceback.format_exc()}")
        raise e
