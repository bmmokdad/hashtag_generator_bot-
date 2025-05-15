import telebot
from telebot import types
import requests
from flask import Flask, request
import os

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

user_keywords = {}

# واجهة البداية: اختيار المنصة
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("تيك توك", callback_data="platform_tiktok"),
        types.InlineKeyboardButton("انستغرام", callback_data="platform_instagram")
    )
    bot.send_message(message.chat.id, "اهلًا في بوت توليد الهاشتاغات! اختر المنصة يلي بدك تشتغل عليها:", reply_markup=markup)

# استقبال الكلمة المفتاحية
@bot.message_handler(func=lambda message: True)
def get_keyword(message):
    user_keywords[message.chat.id] = message.text
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🔥 قوية", callback_data="strength_top"),
        types.InlineKeyboardButton("⭐ متوسطة", callback_data="strength_random"),
        types.InlineKeyboardButton("✨ خفيفة", callback_data="strength_live")
    )
    bot.send_message(message.chat.id, "اختر قوة الهاشتاغات للكلمة المفتاحية:", reply_markup=markup)

# التعامل مع الأزرار
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data.startswith("platform_"):
        platform = call.data.split("_")[1]
        if platform == "instagram":
            bot.answer_callback_query(call.id, "قريبًا! حاليًا نفس نتيجة تيك توك")
        bot.send_message(call.message.chat.id, "اكتب الكلمة المفتاحية يلي بدك تولد هاشتاغات إلها:")

    elif call.data.startswith("strength_"):
        strength = call.data.split("_")[1]
        keyword = user_keywords.get(call.message.chat.id)
        if not keyword:
            bot.send_message(call.message.chat.id, "اكتب الكلمة المفتاحية بالأول!")
            return

        tags = get_hashtags(keyword, strength)
        if not tags:
            bot.send_message(call.message.chat.id, "ما قدرت جيب هاشتاغات، جرّب كلمة تانية!")
            return

        # تنسيق الهاشتاغات
        decorated = decorate_hashtags(tags)

        # رسالة شبابية
        msg = f"جبتلك هاشتاغات {strength} لكلمة '{keyword}':\n\n{decorated}"

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📋 نسخ الهاشتاغات", callback_data=f"copy_{strength}"))
        markup.add(types.InlineKeyboardButton("⬅️ رجوع لاختيار المنصة", callback_data="back_start"))
        bot.send_message(call.message.chat.id, msg, reply_markup=markup)

    elif call.data.startswith("copy_"):
        strength = call.data.split("_")[1]
        keyword = user_keywords.get(call.message.chat.id)
        tags = get_hashtags(keyword, strength)
        bot.send_message(call.message.chat.id, "هاي الهاشتاغات للنسخ السريع:\n" + ' '.join(tags))

    elif call.data == "back_start":
        send_welcome(call.message)

# دالة جلب الهاشتاغات من الموقع
def get_hashtags(keyword, strength):
    url = f"https://www.all-hashtag.com/library/contents/ajax_generator.php?keyword={keyword}&type={strength}"
    try:
        res = requests.post(url)
        tags_raw = res.text.split("<div class='copy-hashtags'>")[1].split("</div>")[0]
        tags = tags_raw.strip().split()
        return tags[:10]  # أول 10 فقط
    except:
        return []

# دالة تزيين الهاشتاغات
def decorate_hashtags(tags):
    decorated = []
    for i, tag in enumerate(tags):
        if i < 3:
            icon = "🔥"
        elif i < 6:
            icon = "⭐"
        else:
            icon = "✨"
        decorated.append(f"{icon} {tag}")
    return '\n'.join(decorated)

# تشغيل السيرفر مع Flask
@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "", 200
    return "بوت الهاشتاغات شغال!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
