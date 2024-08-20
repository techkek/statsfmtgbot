import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import telebot
from config import BOT_TOKEN, HOST, PORT, HOST_LOCAL, PORT_LOCAL, ENV
from commands import register_commands
import threading
from callback import app as flask_app

bot = telebot.TeleBot(BOT_TOKEN)

def run_flask():
    if ENV == "production":
        flask_app.run(host=HOST, port=PORT)
    else:
        flask_app.run(host=HOST_LOCAL, port=PORT_LOCAL)


if __name__ == "__main__":
    register_commands(bot)

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    bot.polling()