
# StatsFMTGBot

StatsFMTGBot is a Telegram bot that interacts with stats.fm to provide users with personalized music statistics and recommendations. The bot supports multiple commands to fetch top songs, albums, artists, and genres, as well as generate random items from a user's library. It also offers language support for English and Italian.

## Features

- Set your stats.fm username.
- Generate random songs, albums, artists, and genres.
- Fetch top items from your library by period (month, 6 months, all time).
- Receive personalized music recommendations.
- Multi-language support (English, Italian).

## Commands

- `/start` - Display a welcome message.
- `/username <username>` - Set your stats.fm username.
- `/random` - Get a random song from your library.
- `/random_artist` - Get a random artist from your library.
- `/random_album` - Get a random album from your library.
- `/random_genre` - Get a random genre from your library.
- `/top<number><period>` - Get your top tracks (e.g., `/top10m`, `/top50hy`, `/top100lt`).
- `/albums<number><period>` - Get your top albums.
- `/artists<number><period>` - Get your top artists.
- `/genres<number><period>` - Get your top genres.
- `/recommend` - Get personalized song and album recommendations.
- `/language <code>` - Set the bot's language (en, it).
- `/help` - Show the help message with all available commands.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/techkek/statsfmtgbot.git
   cd statsfmtgbot
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the bot:
   - Edit config.py with your token

## Running the Bot

To start the bot locally:
```bash
python bot.py
```

Or using Docker:
```bash
docker compose build -d --build
```

## License

This project is licensed under the MIT License.
