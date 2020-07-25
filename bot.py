# -*- coding: utf-8 -*-
import sys

import config
import mysql.connector
import telebot
from cryptography.fernet import Fernet
from mysql.connector import errorcode, IntegrityError
from telebot import types

# cryptography
cipher_key = Fernet.generate_key()  # APM1JDVgT8WDGOWBgQv6EIhvxl4vDYvUnVdg-Vjdt0o=
cipher = Fernet(cipher_key)

# cryptography ends there


bot = telebot.TeleBot(config.Token)

# Connecting to a database
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="crypt"
    )
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
        sys.exit()
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
        sys.exit()
    else:
        print(err)
        sys.exit()
# Initialization of table
cursor = db.cursor()
cursor.execute("""Create TABLE IF NOT EXISTS users(
id INT primary key AUTO_INCREMENT,
crypt VARCHAR(255),
user_id INT UNIQUE
)""")


# for every user
class User:
    def __init__(self, user_id, crypt):
        self.user_id = user_id,
        self.crypt = crypt


# Добавление в базу данных
def add(user):
    try:
        sql = """INSERT INTO users (user_id, crypt) \
                                          VALUES (%s, %s)"""
        val = user.user_id[0], user.crypt
        cursor.execute(sql, val)
        db.commit()
    except IntegrityError:
        pass


# Начинается крипта и работа с ней
def encrypt(message):
    text = message.text.encode()
    encrypted_text = cipher.encrypt(text)
    bot.send_message(message.chat.id, encrypted_text)


def decrypt(message):
    text = message.text.encode()
    decrypted_text = cipher.decrypt(text)
    bot.send_message(message.chat.id, decrypted_text)


# Крипта всё
# работа с запросами
def format(message, forma=""):
    if message is not None:
        msg = bot.send_message(message.chat.id, 'Please, send me your text: ')
        # добавление в базу данных______
        user_id = message.from_user.id
        user = User(user_id=user_id, crypt="В разработке")
        add(user)
        # _____________
        if forma == 'Encrypt':
            bot.register_next_step_handler(msg, encrypt)

        elif forma == 'Decrypt':
            bot.register_next_step_handler(msg, decrypt)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Encrypt")
    item2 = types.KeyboardButton("Decrypt")
    markup.add(item1, item2)
    bot.reply_to(message,
                 "Howdy, partner! I'll service you as the encrypter/decrypter.\nKey for encryption is the same for decryption; they're generating randomly every single time.\nIf you want me to encrypt something, send me 'encrypt', if you want me to decrypt, send me 'decrypt'. ",
                 parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=["text"])
def cipher_alg_choice(message):
    if message.chat.type == 'private':
        if message.text == 'Encrypt':
            format(message, forma='Encrypt')

        elif message.text == 'Decrypt':
            format(message, forma='Decrypt')
    else:
        bot.send_message(message.chat.id, 'Choose ONE)!')


# bots options
# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=10)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

if __name__ == "__main__":
    bot.polling()
