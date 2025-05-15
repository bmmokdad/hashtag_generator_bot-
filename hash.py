import telebot
from flask import Flask, request
import nltk
import re
import string
import random

# تحميل قاموس الكلمات الإنجليزية
nltk.download('words')
from nltk.corpus import words
english_vocab = set(words.words())

# التوكن تبع البوت
TOKEN = '7885976077:AAEKI55zqgfWlruL1bWpAXxBOYx9aZOwy-w'
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# بهدلات عشوائية
insults = [
    "متأكد انك بتعرف تكتب؟ 🌚",
    "شو هي الطلاسم؟ 😂",
    "عجقتني 🌚 صحح كتابتك وفهمني شو بدك 🙄",
    "انا عاوز كلمة مفيدة 🌚",
    "مافهمت شي من هالكلمة 🤦‍♂️"
]

# دالة للتحقق من كون الكلمة عربية
def is_arabic(word):
    return all('\u0600' <= c <= '\u06FF' or c.isspace() for c in word)

# دالة للتحقق من كون الكلمة إنجليزية
def is_english_word(word):
    return word.lower() in english_vocab

# فلترة الكلمات
def is_valid_keyword(word):
    word = word.strip().lower()
    if not word.isalpha():
        return False
    if is_arabic(word):
        return True
    if is_english_word(word):
        return True
    return False

# لما المستخدم يرسل رسالة
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    keyword = message.text.strip()
    if not is_valid_keyword(keyword):
        bot.reply_to(message, random.choice(insults))
        return

    # توليد هاشتاغات مؤقتة
    hashtags = [f"#{keyword}{i}" for i in range(1, 11)]
    hashtags_text = "\n".join(hashtags)
    bot.reply_to(message, f"هاي شوية هاشتاغات:\n\n{hashtags_text}")

# إعداد Webhook
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route('/')
def index():
    return "هاشتاغ بوت شغال 🌐"

# شغّل السيرفر
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url='https://hashtag-generator-bot.onrender.com/' + TOKEN)
    app.run(host="0.0.0.0", port=10000)
