import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import re

TOKEN = '7885976077:AAEKI55zqgfWlruL1bWpAXxBOYx9aZOwy-w'
bot = telebot.TeleBot(TOKEN)

# دالة تجلب هاشتاغات من موقع scraping مجاني (مثال)
def get_hashtags(keyword, strength='high'):
    try:
        # strength ممكن نستخدمها لتصفية لاحقاً أو اختيار عدد أو ترتيب
        url = f'https://best-hashtags.com/hashtag/{keyword}/'
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, 'html.parser')
        # الموقع فيه هاشتاغات في div معين, ناخذ أول 30 تقريباً
        hashtags_section = soup.find('div', {'class': 'tag-box tag-box-v3 margin-bottom-40'})
        if not hashtags_section:
            return None
        tags_text = hashtags_section.text.strip()
        tags = re.findall(r'#\w+', tags_text)
        if not tags:
            return None
        # فلترة حسب قوة الهاشتاغ (high = أول 10, medium = 10 من الوسط, low = آخر 10)
        total = len(tags)
        if strength == 'high':
            selected = tags[:10]
        elif strength == 'medium':
            start = total // 3
            selected = tags[start:start+10]
        else:
            selected = tags[-10:]
        return ' '.join(selected)
    except Exception as e:
        print('Error in get_hashtags:', e)
        return None

# ردود مزح لو كلمة مش مفهومة
funny_replies = [
    "متأكد إنك بتعرف تكتب؟",
    "شو هي الطلاسم؟ عجبتني! صحح كتابتك وفهمني شو بدك.",
    "أنا عاوز كلمة مفيدة مش هيك.",
]

def is_valid_word(word):
    # بسيطة: نتأكد الكلمة أبجدية (عربي أو إنجليزي) بدون رموز
    return re.match(r'^[\u0600-\u06FFa-zA-Z0-9]+$', word) is not None

# البداية: عرض اختيار المنصة (حاليًا بس تيك توك)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('تيك توك')
    # ممكن نضيف هنا انستغرام وفيسبوك مستقبلًا
    markup.add(btn1)
    bot.send_message(message.chat.id, "أهلاً! اختر المنصة اللي بدك هاشتاغات إلها:", reply_markup=markup)

# اختيار المنصة (حاليًا فقط تيك توك)
@bot.message_handler(func=lambda m: m.text in ['تيك توك'])
def platform_chosen(message):
    bot.send_message(message.chat.id, "طيب، اكتبلي كلمة لأجيبلك هاشتاغات قوية. بعدها بدي منك تختار قوة الهاشتاغ (عالٍ، متوسط، منخفض).")

# استقبال كلمة المستخدم وانتظار قوة الهاشتاغ بعدها
user_keywords = {}
user_strengths = {}

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    text = message.text.strip()

    # أوامر تبدأ بـ /
    if text.startswith('/'):
        bot.send_message(message.chat.id, "هاي أمر، استعمل /start عشان ترجع للبداية.")
        return

    # إذا المستخدم ما اختار المنصة بعد
    if message.chat.id not in user_keywords:
        # أول مرة يرسل كلمة بعد اختيار المنصة
        if not is_valid_word(text):
            bot.send_message(message.chat.id, random.choice(funny_replies))
            return
        user_keywords[message.chat.id] = text
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(
            types.InlineKeyboardButton("عالٍ", callback_data="strength_high"),
            types.InlineKeyboardButton("متوسط", callback_data="strength_medium"),
            types.InlineKeyboardButton("منخفض", callback_data="strength_low"),
        )
        bot.send_message(message.chat.id, "اختار قوة الهاشتاغ:", reply_markup=markup)
        return

    # إذا أرسل كلمة جديدة بدل يختار قوة، نعطيه تنبيه ويرجع يختار قوة
    if message.chat.id in user_keywords and message.chat.id not in user_strengths:
        bot.send_message(message.chat.id, "اختار قوة الهاشتاغ من الأزرار تحت، أو اكتب /start للبداية من جديد.")
        return

# استقبال اختيار قوة الهاشتاغ من الأزرار
@bot.callback_query_handler(func=lambda call: call.data.startswith('strength_'))
def callback_strength(call):
    strength = call.data.split('_')[1]
    chat_id = call.message.chat.id

    if chat_id not in user_keywords:
        bot.answer_callback_query(call.id, "أول شي اكتب كلمة.")
        return

    user_strengths[chat_id] = strength
    keyword = user_keywords[chat_id]

    hashtags = get_hashtags(keyword, strength)
    if not hashtags:
        bot.send_message(chat_id, "ما قدرت أجيب هاشتاغات، جرب كلمة ثانية.")
    else:
        bot.send_message(chat_id, f"هاي شوية هاشتاغات لقوة '{strength}':\n{hashtags}")

    # بعد الرد ننظف بيانات المستخدم عشان يبدأ من جديد
    user_keywords.pop(chat_id)
    user_strengths.pop(chat_id)

import random

bot.infinity_polling()
