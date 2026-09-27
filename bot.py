import telebot
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- CONFIG ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")

if not BOT_TOKEN or not TMDB_API_KEY:
    raise ValueError("BOT_TOKEN and TMDB_API_KEY must be set in .env file")

bot = telebot.TeleBot(BOT_TOKEN)

def search_movie(query):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}&language=en-US"
    try:
        r = requests.get(url, timeout=10).json()
        if r.get('results'):
            return r['results'][0] # first result
    except requests.RequestException as e:
        print(f"Error searching movie: {e}")
    return None

def get_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=credits&language=en-US"
    try:
        return requests.get(url, timeout=10).json()
    except requests.RequestException as e:
        print(f"Error fetching movie details: {e}")
        return {}

@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.reply_to(message,
        "🎬 *Cinesubz Movie Info Bot* kiwwa!\n\n"
        "Movie ekaka name eka type karapan machan.\n"
        "Ex: `Avatar`, `Jailer 2`, `Vada Chennai`\n\n"
        "Mama poster + story + cast + rating okkoma genath dennam.",
        parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def handle_movie(message):
    query = message.text.strip()
    if len(query) < 2:
        return

    bot.send_chat_action(message.chat.id, 'typing')
    movie = search_movie(query)

    if not movie:
        bot.reply_to(message, f"'{query}' kiyala movie ekak hambune na machan 😔. Spelling eka balapan.")
        return

    details = get_movie_details(movie['id'])

    # Data tika
    title = details.get('title', 'N/A')
    year = details.get('release_date', '')[:4]
    rating = details.get('vote_average', 'N/A')
    runtime = details.get('runtime', 'N/A')
    overview = details.get('overview', 'No overview')[:800]
    poster_path = details.get('poster_path')

    # Cast 5 denek
    cast_list = details.get('credits', {}).get('cast', [])[:5]
    cast_names = ", ".join([c['name'] for c in cast_list]) if cast_list else "N/A"

    caption = (
        f"🎬 *{title} ({year})*\n"
        f"⭐ Rating: {rating}/10\n"
        f"⏱ Runtime: {runtime} min\n"
        f"🎭 Cast: {cast_names}\n\n"
        f"📖 *Story:*\n{overview}...\n\n"
        f"🔗 More: https://www.themoviedb.org/movie/{details.get('id')}"
    )

    if poster_path:
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        bot.send_photo(message.chat.id, poster_url, caption=caption, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, caption, parse_mode="Markdown")

if __name__ == "__main__":
    print("Bot running... Cinesubz Bot start una!")
    bot.polling(none_stop=True)
