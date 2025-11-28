
import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# -------------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
# -------------------

# Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8208653042
SHEET_NAME = "prazdnik"
SERVICE_ACCOUNT_FILE = "service_account.json"

# Google Sheets авторизация
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
gc = gspread.authorize(credentials)

# Открываем таблицу
try:
    sheet = gc.open(SHEET_NAME).sheet1
except gspread.SpreadsheetNotFound:
    sheet = gc.create(SHEET_NAME).sheet1
    sheet.append_row(["Ім'я", "Прізвище", "Прийду/Не прийду"])

# -------------------
# Хэндлеры
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🎉 Прийду", "❌ Не прийду"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Привіт! 😊 Введи своє ім'я та прізвище через пробіл, а потім обери варіант 👇",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.message.from_user.id

    if text in ["🎉 Прийду", "❌ Не прийду"]:
        if "last_name" in context.user_data and "first_name" in context.user_data:
            # записуємо в Google Sheet
            sheet.append_row([context.user_data["first_name"], context.user_data["last_name"], text])
            await update.message.reply_text("Дякую! Твій вибір збережено 🎄🎁", reply_markup=ReplyKeyboardRemove())
        else:
            await update.message.reply_text("Спочатку введи своє ім'я та прізвище 😅")
    else:
        # припускаємо, що ввели ім'я та прізвище
        parts = text.split()
        if len(parts) >= 2:
            context.user_data["first_name"] = parts[0]
            context.user_data["last_name"] = " ".join(parts[1:])
            keyboard = [["🎉 Прийду", "❌ Не прийду"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text("Обери варіант 🎄:", reply_markup=reply_markup)
        else:
            await update.message.reply_text("Будь ласка, введи ім'я та прізвище через пробіл 😅")

# -------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущено! 🎅❄️")
    app.run_polling()

if __name__ == "__main__":
    main()
