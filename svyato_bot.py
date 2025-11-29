import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import gspread
from google.oauth2.service_account import Credentials

# ------------------- ЛОГИ -------------------
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ------------------- НАСТРОЙКИ -------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
SHEET_NAME = os.getenv("SHEET_NAME", "prazdnik")
SERVICE_ACCOUNT_FILE = "service_account.json"
SERVICE_JSON = os.getenv("SERVICE_JSON")

if not SERVICE_JSON:
    raise ValueError("❌ SERVICE_JSON не найден! Добавь его в Render → Environment.")

# ------------------- СОЗДАЕМ ФАЙЛ SERVICE ACCOUNT -------------------
with open(SERVICE_ACCOUNT_FILE, "w", encoding="utf-8") as f:
    f.write(SERVICE_JSON)

# ------------------- GOOGLE SHEETS -------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
gc = gspread.authorize(credentials)

try:
    sheet = gc.open(SHEET_NAME).sheet1
except gspread.SpreadsheetNotFound:
    sheet = gc.create(SHEET_NAME).sheet1
    sheet.append_row(["Ім'я", "Прізвище", "Статус"])

# ------------------- ХЭНДЛЕРЫ -------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🎉 Прийду", "❌ Не прийду"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привіт! 😊\nВведи своє ім'я та прізвище, а потім обери варіант нижче 🎄👇",
        reply_markup=markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text in ["🎉 Прийду", "❌ Не прийду"]:
        if "first" in context.user_data and "last" in context.user_data:
            sheet.append_row([
                context.user_data["first"],
                context.user_data["last"],
                text
            ])
            await update.message.reply_text(
                "Супер! 🎅 Твоя відповідь записана 🎁",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text("Спочатку введи ім'я та прізвище 😉")
        return

    # Разделяем имя и фамилию
    parts = text.split()
    if len(parts) >= 2:
        context.user_data["first"] = parts[0]
        context.user_data["last"] = " ".join(parts[1:])
        await update.message.reply_text("Чудово! 🎄 Тепер обери свій варіант 👇")
    else:
        await update.message.reply_text("Введи ім'я та прізвище через пробіл 😇")

# ------------------- ЗАПУСК БОТА -------------------
def main():
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN не найден! Добавь его в Render → Environment.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущено! 🎄✨🎅")
    app.run_polling()

if __name__ == "__main__":
    main()

