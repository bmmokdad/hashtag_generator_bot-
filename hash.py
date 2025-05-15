from flask import Flask, request
import telebot
import random

TOKEN = "7885976077:AAEKI55zqgfWlruL1bWpAXxBOYx9aZOwy-w"
WEBHOOK_URL = f"https://hashtag-generator-bot.onrender.com/{TOKEN}"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ======== رسائل الفلترة والبهدلة ========
bad_input_responses = [
    "متأكد انك بتعرف تكتب؟ 🌚",
    "شو هي الطلاسم؟ 😂",
    "عجقتني 🌚 صحح كتابتك وفهمني شو بدك 🙄",
    "أنا عاوز كلمة مفيدة 🌚"
]

# ======== دالة توليد هاشتاغات وهمية (تجريبية) ========
def generate_hashtags(keyword, strength="medium"):
    hashtags = []
    base = f"#{keyword}"
    if strength == "low":
        hashtags = [base + str(i) for i in range(1, 11)]
    elif strength == "medium":
        hashtags = [base + "_trend" + str(i) for i in range(1, 11)]
    elif strength == "high":
        hashtags = [base + "_viral" + str(i) for i in range(1, 11)]
    return hashtags

# ======== استقبال الرسائل =========
@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = telebot.types.KeyboardButton("تيك توك")
    markup.add(btn)
    bot.reply_to(message, "اهلا فيك! اختر المنصة يلي بدك تولد هاشتاغات إلها:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "تيك توك")
def ask_keyword(message):
    msg = bot.reply_to(message, "اكتب الكلمة المفتاحية يلي بدك تولد هاشتاغات عنها:")
    bot.register_next_step_handler(msg, ask_strength)

def ask_strength(message):
    keyword = message.text.strip()
    if not keyword.isalnum():
        bot.reply_to(message, random.choice(bad_input_responses))
        return

    markup = telebot.types.InlineKeyboardMarkup()
    for level in ["low", "medium", "high"]:
        markup.add(telebot.types.InlineKeyboardButton(f"قوة {level}", callback_data=f"{level}|{keyword}"))
    bot.send_message(message.chat.id, f"اختر قوة الهاشتاغات للكلمة: {keyword}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    strength, keyword = call.data.split("|")
    hashtags = generate_hashtags(keyword, strength)

    if not hashtags:
        bot.send_message(call.message.chat.id, "ما قدرت جيب هاشتاغات 🌚 جرب كلمة ثانية.")
        return

    text = f"هاشتاغات قوية ({strength}) للكلمة **{keyword}**:\n\n" + "\n".join(hashtags)
    markup = telebot.types.InlineKeyboardMarkup()
    copy_btn = telebot.types.InlineKeyboardButton("📋 نسخ الهاشتاغات", switch_inline_query=keyword)
    markup.add(copy_btn)
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

# ======== إعداد Webhook =========
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "ok", 200

@app.route("/")
def index():
    return "بوت الهاشتاغ شغال تمام 🌚"

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=5000)    keyword = message.text.strip()
    if not handle_keyword(message, keyword):
        return
    # هنانا بتضيف كود جلب الهاشتاغات بناءً على keyword
    # حالياً، رح نرسل رد تجريبي
    bot.reply_to(message, f"كلمة '{keyword}' تمام! هاجيب لك هاشتاغات على طول...")

bot.infinity_polling()
