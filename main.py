import asyncio
from flask import Flask, request
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from mistralai import Mistral
import nest_asyncio

# ==========================
# Настройки
# ==========================
BOT_TOKEN = "8374515324:AAEDAJezf5FZiDQWHehBhAOhG-NB_PiyFC4"
MISTRAL_API_KEY = "FdppZTy7F6gniPkLn90slYBnxyzK53X"
WEBHOOK_URL = "https://@danistairovul.repl.co/webhook"
MODEL = "mistral-large-latest"

# ==========================
# Инициализация
# ==========================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = Mistral(api_key=MISTRAL_API_KEY)

chat_history = {}  # История чата

app = Flask(__name__)

# ==========================
# Обработчики
# ==========================

@dp.message(Command(commands=["start"]))
async def start_handler(message: types.Message):
    await message.answer("Привет! Я ИИ-бот 🤖 Отправь сообщение, и я отвечу.")

@dp.message(F.text)
async def ai_handler(message: types.Message):
    chat_id = message.chat.id

    if chat_id not in chat_history:
        chat_history[chat_id] = [
            {"role": "system", "content": "Ты полезный ассистент, отвечай кратко и по делу."}
        ]

    chat_history[chat_id].append({"role": "user", "content": message.text})

    # Запрос к Mistral
    chat_response = client.chat.complete(
        model=MODEL,
        messages=chat_history[chat_id]
    )
    response_text = chat_response.choices[0].message.content

    chat_history[chat_id].append({"role": "assistant", "content": response_text})

    # Ограничиваем историю до 10 сообщений
    if len(chat_history[chat_id]) > 10:
        chat_history[chat_id] = [chat_history[chat_id][0]] + chat_history[chat_id][-9:]

    await message.answer(response_text)

# ==========================
# Flask webhook endpoint
# ==========================
@app.route("/webhook", methods=["POST"])
async def webhook():
    data = await request.get_json(force=True)
    update = types.Update.model_validate(data)
    await dp.feed_update(bot, update)
    return "ok", 200

# ==========================
# Настройка webhook
# ==========================
async def on_startup():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook установлен: {WEBHOOK_URL}")

# ==========================
# Запуск Flask и бота одновременно
# ==========================
if __name__ == "__main__":
    import threading
    import nest_asyncio
    nest_asyncio.apply()  # Чтобы можно было запускать asyncio в Replit

    # Запуск on_startup в отдельном потоке
    loop = asyncio.get_event_loop()
    loop.run_until_complete(on_startup())

    # Запуск Flask
    app.run(host="0.0.0.0", port=3000)
