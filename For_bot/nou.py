import config
import telebot
from telebot import types
import requests
import logging
import gptik
import json
from for_SQL import SQL

sql = SQL()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w",
)

bot = telebot.TeleBot(token=config.token)

system_content = 'Ты - дружелюбный помощник! Давай подробный ответ на русском языке.'
task = ''
answer = ''
assistant_content = 'Ответь на вопрос:'
max_tokens_in_task = 2048
user = {}

def check(self, user_id):
    result = sql.select_info(user_id)



@bot.message_handler(commands=['debug'])
def send_logs(message):
    with open("log_file.txt", "rb") as f:
        bot.send_document(message.chat.id, f)


@bot.message_handler(commands=['about'])
def about_command(message):
    user_id = message.chat.id
    bot.send_message(user_id, text="Рад, что ты заинтересован_а! Мое предназначение — не оставлять тебя в "
                                   "одиночестве и всячески подбадривать!")

@bot.message_handler(content_types=["video"])
def video_func(message):
    bot.reply_to(message.chat.id, text="Этот контент не поддерживается ботом. \n"
                               "Нажмите /start для перезапуска"
                 )


@bot.message_handler(content_types=["photo"])
def photo_func(message):
    bot.reply_to(message.chat.id, text="Этот контент не поддерживается ботом. \n"
                               "Нажмите /start для перезапуска"
                 )


@bot.message_handler(content_types=["animation"])
def animation_func(message):
    bot.reply_to(message.chat.id, text="Этот контент не поддерживается ботом. \n"
                               "Нажмите /start для перезапуска"
                 )


@bot.message_handler(content_types=["audio"])
def audio_func(message):
    bot.reply_to(message.chat.id, text="Этот контент не поддерживается ботом. \n"
                               "Нажмите /start для перезапуска"
                 )


@bot.message_handler(content_types=["sticker"])
def sticker_func(message):
    bot.reply_to(message.chat.id, text="Этот контент не поддерживается ботом. \n"
                               "Нажмите /start для перезапуска"
                 )
