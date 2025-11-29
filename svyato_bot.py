import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

import gspread
from google.oauth2.service_account import Credentials

# =====================================================
# ЛОГИ
# =====================================================
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# =====================================================
# НАСТРОЙКИ
# =====================================================
BOT_TOKEN = "8214297458:AAGCcvnSdSJtXnySRj6u_BwNIqlpQgCEYWM"
SHEET_NAME = "prazdnik"
SERVICE_ACCOUNT_FILE = "service_account.json"   # Должен лежать в проекте!

# =====================================================
# GOOGLE SHEETS
# =====================================================
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

if not os.path.exists(SERVICE_ACCOUNT_FILE):
    raise FileNotFoundError(
        "❌ Файл service_account.json не найден!\n"
        "Загрузи свой JSON ключ на Render → Secrets → SERVICE_JSON\n"
        "или положи рядом с ботом."
    )

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
gc = gspread.authorize(creds)

# открываем таблицу или создаём новую
try:
    sheet = gc.open(SHEET_NAME).sheet1
except gspread.SpreadsheetNotFound:
    sheet = gc.create(SHEET_NAME).sheet1
    sheet.append_row(["Ім'я", "Прізвище", "Статус"])

# =====================================================
# /start
# =====================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🎉 Прийду", "❌ Не прийду"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привіт! 🎄✨\n"
        "Напиши, будь ласка, своє *ім’я та прізвище*.\n"
        "Потім обери варіант нижче 👇",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# =====================================================
# Обработка сообщений
# =====================================================
async def msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # кнопки
    if text in ["🎉 Прийду", "❌ Не прийду"]:
        if "fname" in context.user_data and "lname" in context.user_data:
            sheet.append_row([
                context.user_data["fname"],
                context.user_data["lname"],
                text
            ])
            await update.message.reply_text(
                "Дякую! 🎅 Твою відповідь збережено! 🎁",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text("Спершу введи ім’я та прізвище 😊")
        return

    # ввод имени
    parts = text.split()
    if len(parts) >= 2:
        context.user_data["fname"] = parts[0]
        context.user_data["lname"] = " ".join(parts[1:])
        await update.message.reply_text(
            "Супер! Тепер обери варіант нижче 🎄👇"
        )
    else:
        await update.message.reply_text(
            "Будь ласка, введи ім’я та прізвище через пробіл 🙂"
        )

# =====================================================
# MAIN
# =====================================================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler))

    print("Бот запущено! 🎄❄️🎁")
    app.run_polling()

if __name__ == "__main__":
    main()

