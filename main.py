import asyncio
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery, Message
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types.message import ContentType

session = AiohttpSession(proxy='http://proxy.server:3128')  # в proxy указан прокси сервер pythonanywhere, он нужен для подключения

TOKEN = '6924307353:AAFvh9QWhOm8vx5z6jIf_u49xmlUGv4dSgY'  # Замените на ваш токен
API = 'c1b2aac246ad72c2775da986a41f7c21'  # Замените на ваш API-ключ OpenWeatherMap

bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()  # Создаём диспетчер


@dp.message(Command("start"))
async def start(message: Message):
    await send_city_selection(message.chat.id)


@dp.callback_query(F.data)
async def callback_query(call: CallbackQuery):
    if call.data == "enter_city":
        await bot.send_message(call.message.chat.id, "Введите название города:")
    elif call.data == "back":
        await send_city_selection(call.message.chat.id)  # Возврат к выбору города
    else:
        await send_weather(call.message.chat.id, call.data)


@dp.message(F.text)
async def get_weather(message: Message):
    city = message.text.strip().lower()
    await send_weather(message.chat.id, city)


async def send_city_selection(chat_id):
    """Отправляет сообщение с выбором города и кнопкой для ввода вручную"""
    markup = InlineKeyboardBuilder()
    markup.add(
        InlineKeyboardButton(text="Москва", callback_data="Москва"),
        InlineKeyboardButton(text="Санкт-Петербург", callback_data="Санкт-Петербург"),
        InlineKeyboardButton(text="Новосибирск", callback_data="Новосибирск"),
    )
    markup.adjust(1)  # Упорядочивание кнопок по 2 в ряд

    await bot.send_message(chat_id, "Выберите город или введите название вручную:", reply_markup=markup.as_markup())


async def send_weather(chat_id, city):
    """Получает и отправляет погоду"""
    try:
        res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
        data = res.json()

        if res.status_code == 200:
            weather = data['weather'][0]['description']
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']

            response = (f"🌍 Погода в {city.capitalize()}:\n"
                        f"🌡 Температура: {temp}°C\n"
                        f"🤒 Ощущается как: {feels_like}°C\n"
                        f"💧 Влажность: {humidity}%\n"
                        f"☁️ Состояние: {weather.capitalize()}")

            # Кнопки "Обновить", "Ввести город заново", "Купить мне кофе" (ссылка на другого бота) и "Назад"
            markup = InlineKeyboardBuilder()
            markup.add(
                InlineKeyboardButton(text="🔄 Обновить", callback_data=city),
                InlineKeyboardButton(text="📝 Ввести город заново", callback_data="enter_city"),
                InlineKeyboardButton(text="☕ Купить мне кофе", url='https://t.me/kofeemeBot'),
            )
            markup.adjust(1)  # Упорядочивание кнопок по 2 в ряд

        else:
            response = "❌ Город не найден. Введите корректное название."
            markup = None

    except Exception:
        response = "⚠️ Ошибка при получении данных о погоде. Попробуйте позже."
        markup = None

    await bot.send_message(chat_id, response, reply_markup=markup.as_markup() if markup else None)


async def main():
    """Функция запуска бота"""
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())