Python 3.14.0 (tags/v3.14.0:ebf955d, Oct  7 2025, 10:15:03) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import os
import json
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import gspread
from google.oauth2.service_account import Credentials

# ------------------------ ЛОГИ ------------------------
logging.basicConfig(level=logging.INFO)
... logger = logging.getLogger(__name__)
... 
... # ------------------------ ПЕРЕМЕННЫЕ ------------------------
... BOT_TOKEN = os.getenv("BOT_TOKEN")
... SERVICE_JSON = os.getenv("SERVICE_JSON")
... SHEET_NAME = os.getenv("SHEET_NAME", "prazdnik")
... ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
... 
... SERVICE_ACCOUNT_FILE = "service_account.json"
... 
... if not SERVICE_JSON:
...     raise ValueError("❌ SERVICE_JSON не найден! Добавь его в Render → Environment.")
... 
... # Создаём ключевой JSON-файл
... with open(SERVICE_ACCOUNT_FILE, "w", encoding="utf-8") as f:
...     f.write(SERVICE_JSON)
... 
... # ------------------------ GOOGLE SHEETS ------------------------
... scopes = ["https://www.googleapis.com/auth/spreadsheets",
...           "https://www.googleapis.com/auth/drive"]
... 
... credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
... gc = gspread.authorize(credentials)
... 
... try:
...     sheet = gc.open(SHEET_NAME).sheet1
... except gspread.SpreadsheetNotFound:
...     sheet = gc.create(SHEET_NAME).sheet1
...     sheet.append_row(["Ім'я", "Прізвище", "Статус"])
... 
... # ------------------------ ХЭНДЛЕРЫ БОТА ------------------------
... async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
...     keyboard = [["🎉 Прийду", "❌ Не прийду"]]
... 
...     await update.message.reply_text(
...         "Привіт, друже! 😊🎄\n"
...         "Введи своє ім’я та прізвище, а потім обери варіант 👇",
...         reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # Выбор статуса
    if text in ["🎉 Прийду", "❌ Не прийду"]:
        if not ("first" in context.user_data and "last" in context.user_data):
            await update.message.reply_text("Спочатку введи ім’я та прізвище 😉")
            return

        sheet.append_row([
            context.user_data["first"],
            context.user_data["last"],
            text
        ])

        await update.message.reply_text(
            "Супер! 🎁 Твій вибір записано! 🎅",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    # Имя + фамилия
    parts = text.split()
    if len(parts) < 2:
        await update.message.reply_text("Введи *ім’я та прізвище* через пробіл, друже 😊", parse_mode="Markdown")
        return

    context.user_data["first"] = parts[0]
    context.user_data["last"] = " ".join(parts[1:])

    keyboard = [["🎉 Прийду", "❌ Не прийду"]]

    await update.message.reply_text(
        "Добре! Тепер обери свій варіант 🎄👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ------------------------ ЗАПУСК ------------------------
def main():
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN не найден! Добавь его в Render → Environment.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот працює! 🎄✨🎅")
    app.run_polling()

if __name__ == "__main__":
    main()
