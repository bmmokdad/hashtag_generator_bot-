import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup

TOKEN = "توكن البوت هون"
bot = telebot.TeleBot(TOKEN)

# تخزين المنصات المختارة لكل مستخدم
user_platforms = {}

def get_hashtags(keyword):
    url = f"https://tiktokhashtags.com/search?q={keyword.replace(' ', '+')}"
    headers = { "User-Agent": "Mozilla/5.0" }
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        return ["فشل بجلب الهاشتاغات"]

    soup = BeautifulSoup(r.text, "html.parser")
    tags_div = soup.find("div", class_="tag-box")

    if not tags_div:
        return ["ما لقيت هاشتاغات لهالكلمة"]

    tags = [tag.text.strip() for tag in tags_div.find_all("a")]
    return tags[:15]

@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    tiktok_btn = types.KeyboardButton("تيك توك")
    # رح نضيف لاحقًا انستغرام وفيسبوك
    markup.add(tiktok_btn)
    bot.send_message(message.chat.id, "اختر المنصة يلي بدك توليد هاشتاغات إلها:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["تيك توك"])
def set_platform(message):
    user_platforms[message.chat.id] = message.text
    bot.send_message(message.chat.id, "تمام، بعتلي الكلمة المفتاحية لجبلك الهاشتاغات.")

@bot.message_handler(func=lambda m: True)
def handle_keyword(message):
    platform = user_platforms.get(message.chat.id)
    if not platform:
        bot.send_message(message.chat.id, "أول شي اختار المنصة يلي بدك الهاشتاغات إلها.")
        return

    keyword = message.text
    hashtags = get_hashtags(keyword)
    bot.send_message(message.chat.id, "\n".join(hashtags))

bot.polling()
