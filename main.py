import telebot
import requests
import os
from flask import Flask
from threading import Thread

# SOZLAMALAR (Render'dan olinadi)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
TMDB_API_KEY = os.environ.get('TMDB_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "Kino Bot Tayyor!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# TMDB dan trenddagi kinolarni olish
def get_trending():
    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={TMDB_API_KEY}&language=uz-UZ"
    try:
        response = requests.get(url).json()
        return response.get('results', [])[:5]
    except: return []

# Kino qidirish funksiyasi
def search_movie(query):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}&language=uz-UZ"
    try:
        response = requests.get(url).json()
        return response.get('results', [])
    except: return []

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔥 Trenddagi kinolar")
    bot.send_message(message.chat.id, "Kino botga xush kelibsiz! 🎬\n\nKino nomini yozing yoki trendlarni ko'ring:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🔥 Trenddagi kinolar")
def trending(message):
    movies = get_trending()
    if not movies:
        bot.send_message(message.chat.id, "Hozircha ma'lumot olib bo'lmadi.")
        return
    for movie in movies:
        text = f"🍿 *{movie.get('title')}*\n⭐️ Reyting: {movie.get('vote_average')}\n📅 Yil: {movie.get('release_date')}"
        poster = movie.get('poster_path')
        if poster:
            bot.send_photo(message.chat.id, f"https://image.tmdb.org/t/p/w500{poster}", caption=text, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    query = message.text
    if query == "🔥 Trenddagi kinolar": return
    bot.send_message(message.chat.id, "🔎 Qidirilmoqda...")
    results = search_movie(query)
    if results:
        movie = results[0]
        text = f"🎬 *{movie.get('title')}*\n\n⭐️ Reyting: {movie.get('vote_average')}\n📅 Yil: {movie.get('release_date')}\n\n📝 Ma'lumot: {movie.get('overview')[:400]}..."
        poster = movie.get('poster_path')
        if poster:
            bot.send_photo(message.chat.id, f"https://image.tmdb.org/t/p/w500{poster}", caption=text, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, text, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Topilmadi. 😔")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
