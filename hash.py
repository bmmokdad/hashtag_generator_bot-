import telebot
from telebot import types
from flask import Flask, request
import os

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# توليد الهاشتاغات حسب القوة
def generate_hashtags(keyword, level):
    keyword = keyword.lower().strip().replace(" ", "")
    base_tags = {
        'low': ['love', 'like', 'fun'],
        'medium': ['viral', 'trend', 'explore'],
        'high': ['tiktok', 'foryou', 'foryoupage', 'fyp', '2025', 'shorts', 'reels']
    }
    tags = base_tags.get(level, [])
    hashtags = [f"#{keyword}"]
    for tag in tags:
        hashtags.append(f"#{keyword}{tag}")
        hashtags.append(f"#{tag}{keyword}")
    return hashtags[:10]

# رسالة البدء
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("تيك توك")
    markup.add(btn1)
    bot.send_message(message.chat.id, "اختار المنصة يلي بدك هاشتاغات إلها:", reply_markup=markup)

# اختيار المنصة
@bot.message_handler(func=lambda msg: msg.text == "تيك توك")
def ask_keyword(message):
    msg = bot.send_message(message.chat.id, "اكتب الكلمة المفتاحية يلي بدك هاشتاغات عنها:")
    bot.register_next_step_handler(msg, ask_strength)

# عرض خيارات القوة
def ask_strength(message):
    keyword = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("قوة ضعيفة", callback_data=f"low|{keyword}"),
        types.InlineKeyboardButton("قوة متوسطة", callback_data=f"medium|{keyword}"),
        types.InlineKeyboardButton("قوة قوية", callback_data=f"high|{keyword}")
    )
    bot.send_message(message.chat.id, "اختار قوة الهاشتاغات:", reply_markup=markup)

# توليد الهاشتاغات حسب الخيار
@bot.callback_query_handler(func=lambda call: True)
def send_hashtags(call):
    level, keyword = call.data.split("|")
    hashtags = generate_hashtags(keyword, level)
    text = f"هاشتاغات لكلمة: {keyword} (قوة {level}):\n\n" + "\n".join(hashtags)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("نسخ الهاشتاغات", switch_inline_query= " ".join(hashtags)))

    bot.send_message(call.message.chat.id, text, reply_markup=markup)

# Webhook للـ Render
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route('/')
def index():
    return "البوت شغال تمام"

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"https://hashtag-generator-bot.onrender.com/{TOKEN}")
