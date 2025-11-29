import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# ------------------------------ ЛОГИ ----------------------------------
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------------------- ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ --------------------------
BOT_TOKEN = "8214297458:AAGCcvnSdSJtXnySRj6u_BwNIqlpQgCEYWM"
ADMIN_ID = 8208653042
SHEET_NAME = "prazdnik"
SERVICE_ACCOUNT_FILE = "service_account.json"

# ------------------ СОЗДАЁМ ФАЙЛ GOOGLE JSON --------------------------
if not os.path.exists(SERVICE_ACCOUNT_FILE):
    if os.path.exists("@SvyatoKoprBot.json"):
        # если файл в репо
        with open("@SvyatoKoprBot.json", "r", encoding="utf-8") as src:
            with open("service_account.json", "w", encoding="utf-8") as dst:
                dst.write(src.read())
    else:
        raise FileNotFoundError(
            "Файл @SvyatoKoprBot.json не найден! "
            "Положи его рядом с svyato_bot.py."
        )

# -------------------- GOOGLE SHEETS -----------------------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
gc = gspread.authorize(credentials)

try:
    sheet = gc.open(SHEET_NAME).sheet1
except gspread.SpreadsheetNotFound:
    sheet = gc.create(SHEET_NAME).sheet1
    sheet.append_row(["Ім'я", "Прізвище", "Статус"])

# ----------------------- /start ---------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🎉 Прийду", "❌ Не прийду"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привіт! 😄 Напиши, будь ласка, своє ім'я та прізвище.\n"
        "А потім обери варіант нижче 👇🎄",
        reply_markup=markup
    )

# --------------------- ОБРАБОТКА СООБЩЕНИЙ ----------------------------
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
                "Супер! 🎅 Твоя відповідь збережена 🎁",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text("Спочатку напиши ім'я та прізвище 😅")

    else:
        parts = text.split()
        if len(parts) >= 2:
            context.user_data["first"] = parts[0]
            context.user_data["last"] = " ".join(parts[1:])
            await update.message.reply_text("Чудово! 🎄 Тепер обери варіант 👇")
        else:
            await update.message.reply_text("Напиши ім'я та прізвище через пробіл 😉")

# --------------------------- MAIN --------------------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот працює! 🎄🎅❄️")
    app.run_polling()

if __name__ == "__main__":
    main()
