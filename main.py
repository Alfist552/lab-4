import logging
from aiogram import Bot,Dispatcher, types, executor

logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

API_TOKEN = '8530028740:AAHFx-VOolXfsyG6Z_2J0XjNmC9mtRb1Nm0'
URL_OMDb_TOKEN = 'http://www.omdbapi.com/?i=tt3896198&apikey=5178ecd3'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

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

@dp.message_handler()
async def handle_other_messages(message: types.Message):
    try:
        if message.text:
            response = 'Не распознал вашу команду ❌. Для вывода всех команд нажмите на /help'
            await message.answer(response)

    except Exception as e:
        logger.error(f"Ошибка обработки сообщения: {e}")
        await message.answer("Произошла ошибка, попробуйте еще раз")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)