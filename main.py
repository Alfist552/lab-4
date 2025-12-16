import logging
from aiogram import Bot,Dispatcher, types, executor

logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

API_TOKEN = ''
URL_OMDb_TOKEN = ''

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    try:
        text = """Я - Киношник, бот для помощи поиска фильмов
    Я могу найти:
    * Найти информацию о фильмах
    * Показать его рейтинг
    * Дать краткое описание

Напишите /help для вывода всех команд"""
        await message.answer(text)

    except Exception as e:
        logger.error(f"Ошибка:{e}")
        await message.answer("Ошибка, попробуйте еще раз")

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    try:
        text ="""Список всех команд:
    /search - поиск фильма
    /info - информация о источнике данных
    /start - главное меню"""
        await message.answer(text)

    except Exception as e:
        logger.error(f"Ошибка в /help: {e}")
        await message.answer("Произошла ошибка")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)