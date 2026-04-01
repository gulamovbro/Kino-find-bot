import telebot
import requests
import os
from flask import Flask
from threading import Thread

# SOZLAMALAR
BOT_TOKEN = os.environ.get('BOT_TOKEN')
TMDB_API_KEY = os.environ.get('TMDB_API_KEY') # Yangi kalit uchun

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "Kino Bot is running!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# TMDB dan kino qidirish funksiyasi
def search_movie(query):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}&language=uz-UZ"
    response = requests.get(url).json()
    return response.get('results', [])

# Trenddagi kinolarni olish
def get_trending():
    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={TMDB_API_KEY}&language=uz-UZ"
    response = requests.get(url).json()
    return response.get('results', [:5]) # Top 5 ta kino

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔥 Trenddagi kinolar", "🎲 Tasodifiy kino")
    bot.send_message(message.chat.id, 
                     "Salom! Men kino topuvchi botman. 🎬\n\nKino nomini yozing yoki tugmalardan birini tanlang:", 
                     reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🔥 Trenddagi kinolar")
def trending(message):
    movies = get_trending()
    for movie in movies:
        title = movie.get('title')
        rating = movie.get('vote_average')
        date = movie.get('release_date')
        text = f"🍿 *{title}*\n⭐️ Reyting: {rating}\n📅 Yil: {date}"
        
        poster_path = movie.get('poster_path')
        if poster_path:
            img_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            bot.send_photo(message.chat.id, img_url, caption=text, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def handle_search(message):
    query = message.text
    if query in ["🔥 Trenddagi kinolar", "🎲 Tasodifiy kino"]: return
    
    bot.send_message(message.chat.id, "🔎 Qidirilmoqda...")
    results = search_movie(query)
    
    if not results:
        bot.send_message(message.chat.id, "Afsuski, hech narsa topilmadi. 🤔")
        return

    # Faqat birinchi chiqqan natijani ko'rsatamiz
    movie = results[0]
    title = movie.get('title')
    desc = movie.get('overview')
    rating = movie.get('vote_average')
    date = movie.get('release_date')
    
    text = f"🎬 *{title}*\n\n⭐️ Reyting: {rating}\n📅 Yil: {date}\n\n📝 Ma'lumot: {desc[:300]}..."
    
    poster_path = movie.get('poster_path')
    if poster_path:
        img_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        bot.send_photo(message.chat.id, img_url, caption=text, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
