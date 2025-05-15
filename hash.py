from flask import Flask, request
import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from nltk.corpus import words
from pyarabic.araby import is_arabicrange

API_TOKEN = '7885976077:AAEKI55zqgfWlruL1bWpAXxBOYx9aZOwy-w'
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

WEBHOOK_URL = f"https://your-app-name.onrender.com/{API_TOKEN}"

# فلترة الكلمات غير المفهومة
english_words = set(words.words())

def is_valid_word(word):
    if word.startswith("/"):  # أمر تليجرام
        return True
    if all(is_arabicrange(c) for c in word):
        return len(word) > 1  # لازم تكون كلمة عربية بطول معقول
    if word.lower() in english_words:
        return True
    return False

# توليد هاشتاغات وهمية حسب القوة
def generate_hashtags(base, strength="medium"):
    count = 10
    if strength == "weak":
        return [f"#{base}{i}" for i in range(1, count+1)]
    elif strength == "medium":
        return [f"#{base}{i*10}" for i in range(1, count+1)]
    else:
        return [f"#{base}{i*100}" for i in range(1, count+1)]

# رسالة الترحيب
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلا وسهلا فيك! ابعتلي كلمة مفتاحية لنولدلك هاشتاغات نار")

# استقبال الكلمات
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.strip()

    if not is_valid_word(text):
        replies = [
            "متأكد إنك بتعرف تكتب؟ 🌚",
            "شو هي الطلاسم؟ 😂",
            "عجقتني 🌚 صحح كتابتك وفهمني شو بدك 🙄",
            "انا عاوز كلمة مفيدة 🌚"
        ]
        bot.reply_to(message, replies[hash(text) % len(replies)])
        return

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("قوة ضعيفة", callback_data=f"weak:{text}"),
        InlineKeyboardButton("قوة متوسطة", callback_data=f"medium:{text}"),
        InlineKeyboardButton("قوة خارقة", callback_data=f"strong:{text}")
    )
    bot.reply_to(message, "اختر قوة الهاشتاغات يلي بدك ياها:", reply_markup=keyboard)

# معالجة الضغط عالأزرار
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    strength, word = call.data.split(":")
    hashtags = generate_hashtags(word, strength)
    tags_text = "\n".join(hashtags)

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("نسخ الهاشتاغات", switch_inline_query=tags_text))

    bot.send_message(call.message.chat.id, f"هاي شوية هاشتاغات:\n\n{tags_text}", reply_markup=keyboard)

# إعداد الـ Webhook
@app.route(f"/{API_TOKEN}", methods=["POST"])
def receive_update():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/", methods=["GET"])
def setup_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    return "Webhook has been set!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
