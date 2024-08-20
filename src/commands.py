import random
import re
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import (
    get_user_language,
    get_user_settings,
    set_user_data,
    get_user_setting,
    set_user_setting,
    clear_spotify_token,
    get_user
)
from language import get_text
from api_client import (
    get_all_items,
    format_item_info,
    get_first_last_listen,
    get_total_listening_time,
    get_complex_recommendations,
)
from spotify_utils import (
    get_spotify_auth_url,
    handle_spotify_callback,
    add_track_to_playlist,
)
from utils import send_long_message
from config import AVAILABLE_SETTINGS, ENV, GITHUB_REPO
import traceback


def register_commands(bot):
    try:

        @bot.message_handler(commands=["start"])
        def send_welcome(message):
            if message.text.split() == 1:
                lang = get_user_language(message.chat.id)
                bot.reply_to(message, get_text(lang, "welcome"))
            elif message.text == "/start spotify":
                lang = get_user_language(message.chat.id)
                if get_user_setting(message.chat.id, "spotify-connected", False):
                    bot.reply_to(message, get_text(lang, "spotify_connected_success"))
                else:
                    bot.reply_to(message, get_text(lang, "spotify_connected_error"))
            else:
                lang = get_user_language(message.chat.id)
                bot.reply_to(message, get_text(lang, "welcome"))
            if get_user(message.chat.id) == None:
                set_user_data(message.chat.id, "", "en")

        @bot.message_handler(commands=["settings"])
        def send_settings(message):
            chat_id = message.chat.id
            lang = get_user_language(chat_id)
            bot.send_message(
                chat_id,
                get_text(lang, "settings_message"),
                reply_markup=settings_menu(chat_id, lang),
            )

        @bot.message_handler(commands=["connect_spotify"])
        def connect_spotify(message):
            chat_id = message.chat.id
            lang = get_user_language(chat_id)
            auth_url = get_spotify_auth_url(chat_id)
            bot.reply_to(
                message, get_text(lang, "spotify_connect_instructions", auth_url)
            )

        @bot.message_handler(commands=["spotify_callback"])
        def spotify_callback(message):
            chat_id = message.chat.id
            lang = get_user_language(chat_id)
            try:
                code = message.text.split()[1]
                success = handle_spotify_callback(code, chat_id)
                if success:
                    set_user_setting(chat_id, "spotify-connected", True)
                    bot.reply_to(message, get_text(lang, "spotify_connected_success"))
                else:
                    bot.reply_to(message, get_text(lang, "spotify_connected_error"))
            except IndexError:
                bot.reply_to(message, get_text(lang, "spotify_callback_invalid"))

        @bot.callback_query_handler(
            func=lambda call: call.data.startswith(("toggle_", "edit_"))
        )
        def handle_setting(call):
            chat_id = call.message.chat.id
            lang = get_user_language(chat_id)
            action, setting_name = call.data.split("_")
            if setting_name in AVAILABLE_SETTINGS:
                if (
                    action == "toggle"
                    and AVAILABLE_SETTINGS[setting_name]["type"] == "boolean"
                ):
                    current_value = get_user_setting(
                        chat_id,
                        setting_name,
                        AVAILABLE_SETTINGS[setting_name]["default"],
                    )
                    new_value = not current_value
                    set_user_setting(chat_id, setting_name, new_value)
                    bot.answer_callback_query(
                        call.id, get_text(lang, "settings_updated")
                    )
                elif (
                    action == "toggle"
                    and AVAILABLE_SETTINGS[setting_name]["type"] == "callback"
                ):
                    if setting_name == "spotify-connected":
                        if get_user_setting(chat_id, "spotify-connected", False):
                            set_user_setting(chat_id, "spotify-connected", False)
                            clear_spotify_token(chat_id)
                            bot.answer_callback_query(
                                call.id, get_text(lang, "spotify_disconnected")
                            )
                        else:
                            connect_spotify(call.message)
                            bot.answer_callback_query(call.id)
                    else:
                        bot.send_message(
                            chat_id, get_text(lang, "setting_not_implemented")
                        )
                elif (
                    action == "edit"
                    and AVAILABLE_SETTINGS[setting_name]["type"] == "text"
                ):
                    bot.answer_callback_query(call.id)
                    msg = bot.send_message(
                        chat_id,
                        get_text(
                            lang,
                            "enter_new_value",
                            AVAILABLE_SETTINGS[setting_name]["label"][lang],
                        ),
                    )
                    bot.register_next_step_handler(
                        msg, process_setting_input, setting_name
                    )
                    return
                current_markup = call.message.reply_markup
                new_markup = settings_menu(chat_id, lang)
                differences = False
                for i, row in enumerate(current_markup.keyboard):
                    for j, button in enumerate(row):
                        if button.text != new_markup.keyboard[i][j].text:
                            differences = True
                            break
                if differences:
                    try:
                        bot.edit_message_reply_markup(
                            chat_id, call.message.message_id, reply_markup=new_markup
                        )
                    except Exception as e:
                        bot.edit_message_reply_markup(
                            chat_id, call.message.message_id, reply_markup=current_markup
                        )

        def process_setting_input(message, setting_name):
            chat_id = message.chat.id
            lang = get_user_language(chat_id)
            new_value = message.text.strip()

            set_user_setting(chat_id, setting_name, new_value)
            bot.send_message(
                chat_id,
                get_text(lang, "settings_updated"),
                reply_markup=settings_menu(chat_id, lang),
            )

        @bot.message_handler(commands=["random_artist"])
        def send_random_artist(message):
            chat_id = message.chat.id
            lang = get_user_language(chat_id)
            username = get_user_setting(chat_id, "username", "")

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

                response = f"[{artist_info['name']}](https://stats.fm/artist/{artist_info['stats_id']})\n"
                response += f"{get_text(lang, 'streams').capitalize()}: {artist_info['streams']} - #{artist_info['position']} {get_text(lang, 'mpao')}\n"
                response += f"{get_text(lang, 'first_listen')}: {get_first_last_listen(username, 'artists', artist_info['stats_id'], 'first')}\n"
                response += f"{get_text(lang, 'last_listen')}: {get_first_last_listen(username, 'artists', artist_info['stats_id'], 'last')}\n"
                # response += f"Total listening time: {get_total_listening_time(username, 'artists', artist_info['stats_id'])}\n"

                bot.delete_message(chat_id, temp_message.message_id)

                image = artist_info.get("image")

                if isinstance(image, str):
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
            username = get_user_setting(chat_id, "username", "")

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

                response = f"[{album_info['title']}](https://stats.fm/album/{album_info['stats_id']})\n"
                response += f"{get_text(lang, 'artist').capitalize()}:  [{album_info['artist']}](https://stats.fm/artist/{album_info['artist_id']})\n"
                response += f"{get_text(lang, 'streams').capitalize()}: {album_info['streams']} - #{album_info['position']} {get_text(lang, 'mpao')}\n"
                response += f"{get_text(lang, 'first_listen')}: {get_first_last_listen(username, 'albums', album_info['stats_id'], 'first')}\n"
                response += f"{get_text(lang, 'last_listen')}: {get_first_last_listen(username, 'albums', album_info['stats_id'], 'last')}\n"
                # response += f"Total listening time: {get_total_listening_time(username, 'albums', album_info['stats_id'])}\n"

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
            username = get_user_setting(chat_id, "username", "")
            auto_preview = get_user_setting(
                chat_id, "auto-preview", AVAILABLE_SETTINGS["auto-preview"]["default"]
            )
            if not username:
                bot.reply_to(message, get_text(lang, "set_username_first"))
                return

            temp_message = bot.send_message(chat_id, get_text(lang, "generating_song"))

            all_tracks = get_all_items(username, "", "tracks")

            if all_tracks:
                random_track = random.choice(all_tracks)
                track_info = format_item_info(random_track, "tracks", username)

                response = f"[{track_info['title']}](https://stats.fm/track/{track_info['stats_id']})\n"
                response += f"{get_text(lang, 'artist').capitalize()}: [{track_info['artist']}](https://stats.fm/artist/{track_info['artist_id']})\n"
                response += f"Album: {track_info['album']}\n"
                response += f"{get_text(lang, 'streams').capitalize()}: {track_info['streams']} - #{track_info['position']} {get_text(lang, 'mpao')}\n"
                response += f"{get_text(lang, 'first_listen')}: {get_first_last_listen(username, 'tracks', track_info['stats_id'], 'first')}\n"
                response += f"{get_text(lang, 'last_listen')}: {get_first_last_listen(username, 'tracks', track_info['stats_id'], 'last')}\n"
                # response += f"Total listening time: {get_total_listening_time(username, 'tracks', track_info['stats_id'])}\n"

                bot.delete_message(chat_id, temp_message.message_id)

                if get_user_setting(chat_id, "spotify-connected", False) and track_info["spotify_id"] != "N/A":
                    spotify_button = InlineKeyboardButton(
                        get_text(lang, "save_to_spotify"),
                        callback_data=f"save_spotify_{track_info['spotify_id']}",
                    )
                    markup = InlineKeyboardMarkup().add(spotify_button)
                else:
                    markup = None

                if track_info["album_image"] != "N/A":
                    if markup:
                        bot.send_photo(
                            chat_id,
                            track_info["album_image"],
                            caption=response,
                            parse_mode="Markdown",
                            reply_markup=markup,
                        )
                    else:
                        bot.send_photo(
                            chat_id,
                            track_info["album_image"],
                            caption=response,
                            parse_mode="Markdown",
                        )

                else:
                    if markup:
                        bot.send_message(
                            chat_id,
                            response,
                            parse_mode="Markdown",
                            reply_markup=markup,
                        )
                    else:
                        bot.send_message(chat_id, response, parse_mode="Markdown")

                if track_info["preview_url"] != "N/A" and auto_preview:
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

        @bot.callback_query_handler(
            func=lambda call: call.data.startswith("save_spotify_")
        )
        def save_to_spotify(call):
            chat_id = call.message.chat.id
            lang = get_user_language(chat_id)
            track_id = call.data.split("_")[2]

            success = add_track_to_playlist(chat_id, track_id)
            if success == "already_saved":
                bot.answer_callback_query(call.id, get_text(lang, "track_already_saved"))
            elif success:
                bot.answer_callback_query(
                    call.id, get_text(lang, "track_saved_to_spotify")
                )
            else:
                bot.answer_callback_query(call.id, get_text(lang, "track_save_error"))

        @bot.message_handler(commands=["random_genre"])
        def send_random_genre(message):
            chat_id = message.chat.id
            lang = get_user_language(chat_id)
            username = get_user_setting(chat_id, "username", "")

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

                response = f"[{genre_info['name'].capitalize()}](https://stats.fm/genre/{genre_info['name']})\n"
                response += f"{get_text(lang, 'position')}: #{genre_info['position']}\n"
                response += f"{get_text(lang, 'streams').capitalize()}: {genre_info['streams']}\n"

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
                        message.chat.id, get_user_setting(message.chat.id, "username", ""), lang_code
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
            bot.reply_to(message, get_text(lang, "help_message", GITHUB_REPO), parse_mode="HTML", disable_web_page_preview=True)

        @bot.message_handler(
            func=lambda message: message.text.lower().startswith(
                ("/top", "/albums", "/artists", "/genres")
            )
        )
        def send_top_items(message):
            chat_id = message.chat.id
            lang = get_user_language(chat_id)
            username = get_user_setting(chat_id, "username", "")

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
                        response += f"{item_info['position']}. [{item_info['name']}](https://stats.fm/artist/{item_info['stats_id']}) ({item_info['streams']} {get_text(lang, 'streams')})\n"
                    elif item_type == "genres":
                        response += f"{item_info['position']}. [{item_info['name'].capitalize()}](https://stats.fm/genre/{item_info['name']}) ({item_info['streams']} {get_text(lang, 'streams')})\n"
                    else:
                        response = "Invalid item type\n"
                        bot.delete_message(chat_id, temp_message.message_id)
                        bot.reply_to(message, response, disable_web_page_preview=True)
                        if ENV == "debug":
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
            username = get_user_setting(chat_id, "username", "")

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
                if ENV == "debug":
                    print(f"Error getting recommendations: {e} - {traceback.format_exc()}")

        @bot.message_handler(commands=["github"])
        def send_github(message):
            lang = get_user_language(message.chat.id)
            bot.reply_to(message, get_text(lang, "github", GITHUB_REPO), parse_mode="Markdown")
        
        @bot.message_handler(commands=["report"])
        def send_report(message):
            lang = get_user_language(message.chat.id)
            bot.reply_to(message, get_text(lang, "report", GITHUB_REPO), parse_mode="Markdown")

        @bot.message_handler(commands=["feature"])
        def send_feature(message):
            lang = get_user_language(message.chat.id)
            bot.reply_to(message, get_text(lang, "feature", GITHUB_REPO), parse_mode="Markdown")

        @bot.message_handler(commands=["question"])
        def send_question(message):
            lang = get_user_language(message.chat.id)
            bot.reply_to(message, get_text(lang, "question", GITHUB_REPO), parse_mode="Markdown")
        

    except Exception as e:
        if ENV == "development" or ENV == "debug":
            print(f"Error registering commands: {e} - {traceback.format_exc()}")
        raise e


def settings_menu(chat_id, lang):
    markup = InlineKeyboardMarkup()
    settings = get_user_settings(chat_id)

    for setting_name, setting_info in AVAILABLE_SETTINGS.items():
        current_value = settings.get(setting_name, setting_info["default"])
        if setting_info["type"] == "boolean" or setting_info["type"] == "callback":
            value_text = (
                get_text(lang, "on") if current_value else get_text(lang, "off")
            )
            button_text = f"{setting_info['label'][lang]}: {value_text}"
            markup.row(
                InlineKeyboardButton(
                    button_text, callback_data=f"toggle_{setting_name}"
                )
            )
        elif setting_info["type"] == "text":
            button_text = f"{setting_info['label'][lang]}: {current_value or get_text(lang,'not_set')}"
            markup.row(
                InlineKeyboardButton(button_text, callback_data=f"edit_{setting_name}")
            )

    return markup
