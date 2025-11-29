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
BOT_TOKEN = {
  "type": "service_account",
  "project_id": "enduring-palace-476610-t5",
  "private_key_id": "8f8f6d05b5762b49b187a7b516e1e7fcfe10df83",
  "private_key": {
  "type": "service_account",
  "project_id": "enduring-palace-476610-t5",
  "private_key_id": "f6779e70cc8dab887f9cde285629a689c9c0c153",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDrnsfkA0KylK36\ntFOlTGnSiRH4XUQUzLvBbWUrSRw/eCvDaMYZpbPSd0JYhveYeMpGJvdgwV0e11Z/\n2xYOiTn3RXJW92bwl3uiNg5raXcKY7ZTmJDpQoeOdftBWuPxdS874t7n9wp6L/r1\nBSvih89tD8Qh7U75Wlttw2O1fRZyAiMf7clqA68RY5kq0w6eQReIbF5samr91Sa3\nPhkaPjh9hKT5vQ9YYh0sege35LxXEDXx052j1kPV/MBA6IJQx8ymrmpfLFh5m82H\nXQhlpiY78VPFmQCXu4k8ylv/J0jjXYJOuD9PQn+ArZzZ9gOkcCUroHFzzkCDY6Mh\nE59WKlhJAgMBAAECggEAAZDTDDlXUp95Tn6vRZxt4ZfGlktsXeUEZGMpNnHsbaGL\nTOef1WDMApyHRNZUw98dnPy6TRrL1x4gNYZLrboMuA9ulJRdS0D+cdQBIYaYY2nJ\nNuH/KIWoJ/Kxwjvr4tlgAHpf99Ok7q3t8X3gzkcPwk5GA+GzUiXfEKopOfYEVaqZ\ntBWOrZ/bbeSB9TQ9mtT0QW9+wC4+An2M9fh4yOoFFHRLMqnEMrxML5UEVr1WkpqZ\nrvYhUOx3IbGPHl28Mrpj7O8yb32EAuJQ43yRFqoT3n5OyANuDaQAhyvY/k77Hb/3\nZWOnbV3TjNcysrVw6Ydwf4ffB8idno75iFWcgmTSWQKBgQD920cx2mNJuVes9o0j\nPmU3VXKN8sXYxjjFeuHX6eMnDq7z+QqXL0Ms+C197e4+WzK0IwGsDl4OtpwgkANZ\nw7fQDSIACGrySUwI0go8wX2HZKoPu+9p+kWmFzGGDNseGrXwGb9dwksLaSMiIixr\nR7NLvDvCjNdIOD8PKefi9K+tZQKBgQDtnBWJo+LKAo3rySvfk0JmlUo805XDdUwr\nb9XJC2/wh5kOMvpEIvN8LbawJBc6H58HNYGKrpSvTDv+q2WPvJ/qL6rD33Rke/MG\nXg6QInHJH3o+2jfN1GPb/bKae91nyE/mDrvax06AVpY2lZyOF8E9+Lp4b9ffNVZ9\ncjyUsv4zFQKBgDtYfO9Zp6Z/jtCfnuUjXBQwhKRMohYIWRNJo+yPAAyMcTgV+3TW\nlrS3nCL5cZ3gQh08pdJsVW7JH/y4zh+5Eoqv10f8r8vOeNkDCWOktEznqp4dCF5V\nJN0sROaasMr74Zas3kD0AAk93fnH1WyLCY5mBe54cIewpoVL/argGwXFAoGBAO2O\nKXJM6Yax+xYLMNP8NFy/UVNy7r5V3WtoCkNQLgA6cWliyhepIem7AnUkABzaVHIu\nqm7ukDSacTjyPz3vhanrMj1WgNWdnqF1E/ZCmaRM1jlUjoo4mAXvpMsSn48NE+Sc\nQnA+51skNlYoSjc9xLOiozuaBidg+jG9Lpg0RDTpAoGBAIw9l938CE6IO+OG6mwK\nxQyJH9LZ1OadAsTXMlkr8C8NZ7U0Xh4JUDv+n4JD11ptj6KAFjsjyTDkteTJDfxB\nZK0bBbMZOmVYVVRcHYhIpLZSJOuzOPQ76BdXVpU2mnMczzidWhENcnAZ+oo+tYUM\nqRThTb6t/tED37e3bZuTR2XC\n-----END PRIVATE KEY-----\n",
  "client_email": "id-svyatokoprbot@enduring-palace-476610-t5.iam.gserviceaccount.com",
  "client_id": "108218827090551179199",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/id-svyatokoprbot%40enduring-palace-476610-t5.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
  "client_email": "id-svyatokoprbot@enduring-palace-476610-t5.iam.gserviceaccount.com",
  "client_id": "108218827090551179199",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/id-svyatokoprbot%40enduring-palace-476610-t5.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
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

