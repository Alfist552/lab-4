import logging
import requests
from aiogram import Bot,Dispatcher, types, executor
import os
import json
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

API_TOKEN = '8530028740:AAHFx-VOolXfsyG6Z_2J0XjNmC9mtRb1Nm0'
URL_OMDb_TOKEN = 'http://www.omdbapi.com/?apikey=[5178ecd3]&'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

FAVORITES_FILE = 'favorites.json'
waiting_for_search = {}
last_movies = {}

FIELD_TRANSLATIONS = {
    'Title': '🎬 Название',
    'Year': '📅 Год',
    'Rated': '🔞 Рейтинг',
    'Released': '📆 Дата выхода',
    'Runtime': '⏱️ Длительность',
    'Genre': '🎭 Жанр',
    'Director': '🎥 Режиссер',
    'Writer': '✍️ Сценарист',
    'Actors': '🌟 Актеры',
    'Plot': '📖 Описание',
    'Language': '🌍 Язык',
    'Country': '📍 Страна',
    'Awards': '🏆 Награды',
    'Ratings': '⭐ Рейтинги',
    'Metascore': '📊 Metascore',
    'imdbRating': '⭐ IMDb рейтинг',
    'imdbVotes': '👥 IMDb голоса',
    'imdbID': '🆔 IMDb ID',
    'Type': '🎞️ Тип',
    'DVD': '📀 DVD релиз',
    'BoxOffice': '💰 Кассовые сборы',
    'Production': '🏢 Производство',
    'Website': '🌐 Сайт'
}

def translate_movie_data(movie_data):
    translated = {}

    for key, value in movie_data.items():
        if key in FIELD_TRANSLATIONS:
            new_key = FIELD_TRANSLATIONS[key]
            if isinstance(value, str) and value.upper() == 'N/A':
                translated[new_key] = 'Не указано'
            elif key == 'Ratings' and isinstance(value, list):
                ratings_text = ''
                for rating in value:
                    source = rating.get('Source', '')
                    russian_source = {
                        'Internet Movie Database': 'IMDb',
                        'Rotten Tomatoes': 'Rotten Tomatoes',
                        'Metacritic': 'Metacritic'
                    }.get(source, source)

                    value_rating = rating.get('Value', '')
                    ratings_text += f'• {russian_source}: {value_rating}\n'

                translated[new_key] = ratings_text.strip()
            else:
                translated[new_key] = value
        else:
            translated[key] = value

    return translated

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    try:
        text = """Я - Киношник, бот для помощи поиска фильмов🍿
    Для вас я могу:
    * Найти информацию о фильмах ❓
    * Показать его рейтинг 📈
    * Дать краткое описание ℹ️

Напишите /help для вывода всех команд"""
        await message.answer(text)

    except Exception as e:
        logger.error(f"Ошибка:{e}")
        await message.answer("Ошибка, попробуйте еще раз")

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    try:
        text ="""Список всех команд:
    /search - поиск фильма 🧑‍💻
    /myfav - мои избранные фильмы ❤️
    /info - информация о источнике данныхℹ️
    /start - главное меню"""
        await message.answer(text)

    except Exception as e:
        logger.error(f"Ошибка в /help: {e}")
        await message.answer("Произошла ошибка :( ")

@dp.message_handler(commands=['info'])
async def info_command(message: types.Message):
    try:
        text = """Информация о боте:
    Данные о фильмах предоставляются благодаря сервису OMDb✅
    Рейтинги составлены на основе IMDb, Rotten Tomatoes🍅"""
        await message.answer(text)

    except Exception as e:
        logger.error(f"Ошибка в /info: {e}")
        await message.answer("Произошла ошибка :( ")

@dp.message_handler(commands=['search'])
async def search_command(message: types.Message):
    try:
        await message.answer("Введите название фильма")
        user_id = message.from_user.id
        waiting_for_search[user_id] = True

    except Exception as e:
        logger.error(f"Ошибка в /search: {e}")
        await message.answer("Произошла ошибка")

@dp.message_handler(commands=['myfav'])
async def my_favorites_command(message: types.Message):
    try:
        user_id = message.from_user.id
        favorites = get_favorites(user_id)

        if not favorites:
            await message.answer("У вас пока нет избранных фильмов 😢\nНайдите фильм через /search")
            return

        response = "🎬 Ваши избранные фильмы:\n\n"
        for i, movie in enumerate(favorites, 1):
            response += f"{i}. {movie.get('Title', 'Неизвестно')} ({movie.get('Year', '?')})\n"

        await message.answer(response)

    except Exception as e:
        logger.error(f"Ошибка в /myfav: {e}")
        await message.answer("Ошибка загрузки избранного")

@dp.message_handler(lambda message: message.text in ["❤️ Добавить в избранное", "✅ Уже в избранном", "🔍 Новый поиск"])
async def handle_keyboard_buttons(message: types.Message):
    try:
        user_id = message.from_user.id

        if message.text == "❤️ Добавить в избранное":
            if user_id in last_movies:
                movie_data = last_movies[user_id]
                if add_to_favorites(user_id, movie_data):
                    await message.answer("✅ Фильм добавлен в избранное!", reply_markup=types.ReplyKeyboardRemove())
                else:
                    await message.answer("❌ Фильм уже в избранном", reply_markup=types.ReplyKeyboardRemove())
            else:
                await message.answer("Сначала найдите фильм через /search", reply_markup=types.ReplyKeyboardRemove())

        elif message.text == "🔍 Новый поиск":
            await message.answer("Используйте /search для нового поиска", reply_markup=types.ReplyKeyboardRemove())

        elif message.text == "✅ Уже в избранном":
            await message.answer("Этот фильм уже в вашем избранном!", reply_markup=types.ReplyKeyboardRemove())

    except Exception as e:
        logger.error(f"Ошибка обработки кнопки: {e}")
        await message.answer("Произошла ошибка", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler()
async def handle_other_messages(message: types.Message):
    try:
        user_id = message.from_user.id
        if user_id in waiting_for_search and waiting_for_search[user_id]:
            movie_title = message.text.strip()
            if not movie_title:
                await message.answer("Пожалуйста, введите название фильма.")
                return
            del waiting_for_search[user_id]

            await message.answer(f" Ищу '{movie_title}'...")

            movie_data = search_movie(movie_title)

            if movie_data:
                poster_url = movie_data.get('Poster')
                if poster_url and poster_url != 'N/A':
                    try:
                        await message.answer_photo(poster_url)
                    except Exception as e:
                        logger.error(f"Не удалось отправить постер: {e}")
                result, is_in_fav = format_movie_info(movie_data, user_id = user_id)
                await message.answer(result)

                keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                if not is_in_fav:
                    keyboard.add(KeyboardButton("❤️ Добавить в избранное"))
                else:
                    keyboard.add(KeyboardButton("✅ Уже в избранном"))
                keyboard.add(KeyboardButton("🔍 Новый поиск"))

                last_movies[user_id] = movie_data

                await message.answer("Что делаем дальше?", reply_markup=keyboard)
            else:
                await message.answer(f"❌ Фильм '{movie_title}' не найден")

            await message.answer("🔍 Для нового поиска используйте /search")

        else:
            response = 'Не распознал вашу команду ❌. Для вывода всех команд нажмите на /help'
            await message.answer(response)

    except Exception as e:
        logger.error(f"Ошибка обработки сообщения: {e}")
        await message.answer("Произошла ошибка, попробуйте еще раз")

def search_movie(title):
    try:
        logger.info(f"🔍 Начинаем поиск фильма: '{title}'")

        base_url = URL_OMDb_TOKEN.replace('[', '').replace(']', '')

        encoded_title = title.replace(' ', '+')

        search_url = f"{base_url}t={encoded_title}"

        logger.info(f"📡 Отправляю запрос к API: {search_url}")

        response = requests.get(search_url, timeout=10)

        if response.status_code == 200:
            movie_data = response.json()

            if movie_data.get('Response') == 'True':
                logger.info(f" Фильм найден: '{title}'")
                return movie_data
            else:
                error_message = movie_data.get('Error', 'Неизвестная ошибка')
                logger.warning(f" Фильм не найден: '{title}'. Ошибка: {error_message}")
                return None

        else:
            logger.error(f" Ошибка API: HTTP {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        logger.error(f"⏱️ Таймаут при поиске фильма: '{title}'")
        return None

    except requests.exceptions.ConnectionError:
        logger.error(f" Ошибка подключения при поиске: '{title}'")
        return None

    except Exception as e:
        logger.error(f" Неожиданная ошибка при поиске '{title}': {e}")
        return None

def format_movie_info(movie_data, user_id = None):
    try:
        translated = translate_movie_data(movie_data)

        info = f"🎬{translated.get('🎬 Название', 'Неизвестно')} ({translated.get('📅 Год', 'Неизвестно')})\n\n"
        info += f"⏱️Длительность: {translated.get('⏱️ Длительность', 'Неизвестно')}\n"
        info += f"🎭Жанр: {translated.get('🎭 Жанр', 'Неизвестно')}\n"
        info += f"⭐IMDb: {translated.get('⭐ IMDb рейтинг', 'Нет оценки')}\n\n"
        info += f"🎥Режиссер: {translated.get('🎥 Режиссер', 'Неизвестно')}\n"
        info += f"🌟Актеры: {translated.get('🌟 Актеры', 'Неизвестно')}\n\n"
        info += f"📖Описание: {translated.get('📖 Описание', 'Нет описания')}"

        is_in_fav = False
        if user_id:
            favorites = get_favorites(user_id)
            for fav in favorites:
                if fav.get('imdbID') == movie_data.get('imdbID'):
                    is_in_fav = True
                    break

        return info,is_in_fav

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return "Ошибка при обработке данных"

def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        try:
            with open(FAVORITES_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_favorites(favorites):
    with open(FAVORITES_FILE, 'w') as f:
        json.dump(favorites, f)

def add_to_favorites(user_id, movie_data):
    favorites = load_favorites()
    user_id_str = str(user_id)

    if user_id_str not in favorites:
        favorites[user_id_str] = []

    for movie in favorites[user_id_str]:
        if movie.get('imdbID') == movie_data.get('imdbID'):
            return False

    favorites[user_id_str].append(movie_data)
    save_favorites(favorites)
    return True

def get_favorites(user_id):
    favorites = load_favorites()
    return favorites.get(str(user_id), [])

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)