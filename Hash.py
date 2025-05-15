import telebot
import os
from flask import Flask, request

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# رسالة البداية مع زر اختيار المنصة
@bot.message_handler(commands=['start'])
def start_message(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("تيك توك")
    bot.send_message(message.chat.id, "أهلا فيك، اختر المنصة يلي بدك هاشتاغات إلها:", reply_markup=markup)

# الرد بعد اختيار المنصة
@bot.message_handler(func=lambda m: True)
def get_hashtags(message):
    if message.text == "تيك توك":
        bot.reply_to(message, "اكتبلي الكلمة المفتاحية يلي بدك هاشتاغات عنها")
    else:
        keyword = message.text
        # توليد هاشتاغات وهمية حالياً
        fake_hashtags = [f"#{keyword}", f"#{keyword}tok", f"#{keyword}viral", f"#{keyword}2025"]
        hashtags_text = " ".join(fake_hashtags)
        bot.send_message(message.chat.id, f"هاي شوية هاشتاغات مقترحة:\n\n{hashtags_text}")

# Webhook handler
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

# صفحة رئيسية بسيطة
@app.route("/")
def index():
    return "Bot is running!"

# إعداد Webhook عند تشغيل السيرفر
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    HEROKU_URL = "https://hashtag-generator-bot.onrender.com"

    bot.remove_webhook()
    bot.set_webhook(url=f"{HEROKU_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
