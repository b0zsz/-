"""
Telegram-бот: конвертер валют.

Что умеет:
- отвечает на /start приветствием
- принимает сообщение вида "100 USD RUB" и считает конвертацию
- если формат сообщения неправильный — вежливо просит повторить

Курсы валют пока захардкожены (фиксированные числа).

"""

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from dotenv import load_dotenv
import os

load_dotenv()  # читает файл .env и подгружает переменные
BOT_TOKEN = os.getenv("BOT_TOKEN")  # достаёт значение по имени


# Захардкоженные курсы валют относительно USD.
# Это словарь: ключ - код валюты, значение - сколько это в USD.
RATES_TO_USD = {
    "USD": 1.0,
    "RUB": 0.011,   # 1 рубль = 0.011 доллара (примерно)
    "EUR": 1.08,    # 1 евро = 1.08 доллара (примерно)
    "KZT": 0.0019,  # 1 тенге = 0.0019 доллара (примерно)
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    await update.message.reply_text(
        "Привет! Я конвертер валют.\n\n"
        "Напиши сообщение в формате:\n"
        "100 USD RUB\n\n"
        "Это значит: перевести 100 долларов в рубли.\n"
        f"Доступные валюты: {', '.join(RATES_TO_USD.keys())}"
    )


async def convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик обычных текстовых сообщений — пытается их сконвертировать."""
    text = update.message.text.strip()
    parts = text.split()

    # Проверяем, что сообщение состоит ровно из трёх частей
    if len(parts) != 3:
        await update.message.reply_text(
            "Не понял формат. Пример: 100 USD RUB"
        )
        return

    amount_str, from_currency, to_currency = parts
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    # Проверяем, что первая часть - это число
    try:
        amount = float(amount_str)
    except ValueError:
        await update.message.reply_text(
            "Первым должно идти число. Пример: 100 USD RUB"
        )
        return

    # Проверяем, что валюты нам известны
    if from_currency not in RATES_TO_USD or to_currency not in RATES_TO_USD:
        await update.message.reply_text(
            f"Не знаю такую валюту. Доступные: {', '.join(RATES_TO_USD.keys())}"
        )
        return

    # Сама конвертация: сначала переводим в USD, потом из USD в нужную валюту
    amount_in_usd = amount * RATES_TO_USD[from_currency]
    result = amount_in_usd / RATES_TO_USD[to_currency]

    await update.message.reply_text(
        f"{amount} {from_currency} = {result:.2f} {to_currency}"
    )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, convert))

    print("Бот запущен. Останови через Ctrl+C.")
    app.run_polling()


if __name__ == "__main__":
    main()