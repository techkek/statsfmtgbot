import telebot
from config import BOT_TOKEN
from commands import register_commands

bot = telebot.TeleBot(BOT_TOKEN)

if __name__ == "__main__":
    register_commands(bot)
    bot.polling()