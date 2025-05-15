import telebot
import random
from pyarabic.araby import is_arabicrange

TOKEN = "7885976077:AAEKI55zqgfWlruL1bWpAXxBOYx9aZOwy-w"
bot = telebot.TeleBot(TOKEN)

def is_arabic_word(word):
    return all(is_arabicrange(c) for c in word) and len(word) >= 3

def is_english_word(word):
    return word.isalpha() and word.isascii() and len(word) >= 3

def handle_keyword(message, keyword):
    if not (is_arabic_word(keyword) or is_english_word(keyword)):
        bad_responses = [
            "متاكد انك بتعرف تكتب ؟ 🌚",
            "شو هي الطلاسم ؟😂",
            "عجقتني 🌚 صحح كتابتك وفهمني شو بدك 🙄",
            "انا عاوز كلمة مفيدة 🌚"
        ]
        bot.reply_to(message, random.choice(bad_responses))
        return False
    return True

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('تيك توك')
    btn2 = telebot.types.KeyboardButton('إنستغرام (قريباً)')
    btn3 = telebot.types.KeyboardButton('فيسبوك (قريباً)')
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, "أهلاً! اختر المنصة اللي بدك هاشتاغاتها:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def process_message(message):
    keyword = message.text.strip()
    if not handle_keyword(message, keyword):
        return
    # هنانا بتضيف كود جلب الهاشتاغات بناءً على keyword
    # حالياً، رح نرسل رد تجريبي
    bot.reply_to(message, f"كلمة '{keyword}' تمام! هاجيب لك هاشتاغات على طول...")

bot.infinity_polling()
