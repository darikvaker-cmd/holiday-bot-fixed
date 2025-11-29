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
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDDp+ikAmig6tnV\nE1kUwduLbk+Hnh4zxM1r8v/YlO/l2towWl48jpYdkUy3wrhqB4OnjT1JRbvmyYx+\nRxMcD0iGfWZ5+9WclJxrYPw48snAIUIfUbqrfLR8m9yVlb8ybxa2Mc4/BYnIqC5l\n7M1iuUpac0Uu75a+AC+ff1tRQpb2vDGNcHHf0xCiPaDXsKfMjEhvRApLALwNdJsh\n9tT86XNQv6ipdlA3IrP4wBqbMQR7WgGvrxF0ZIkvS0A5BQQs3f+w1XHWDX5FnAIn\nJRq89f4wt7YA03a4Dx7y+rQjttBTImnmtwoK3AR06ZqjVE0gvr12vURRczqD29hl\nmNnBErVjAgMBAAECggEADmh9iyJlm8AKYD9nVnjQ1uuTLhIDTbL8S6rz6KT4e6Kf\ntw2DQLi2rku7whE0AmmLlO746JNFkJZ0Dafkl4g6l4jW3zx1O8LSjV0cMIIUlbJS\noRAkNn+y94raINE2aMY3KR3xfxZEfMMsfjNaNp8dg3FXUsBbB009NI+COobfAMwJ\njYZD3cDFntZqmi15IHG0p8PFiNzXS34cZyBQberols/xGRw+zy/lwrz5CeIbzqkY\nJgRd6BL3Aa131ZbwdAIg681sQUeB4G14Lai+cthCFcZVFuFWUzRzogGTUJQ2Sicz\ner+h57DUsx302UHcqwtAiG0bdU3zHdLdH74sLpDjmQKBgQD7LSMZdXDUxzK1BY+g\n8/CzlH81ad0sw1kJY4Fwh9PCSgKNef/RRErs7LYMqlAjgBUzNMxaSg6ER7xLGL62\nxoMgeOIJMTofmWdWNG5/syw3mzsowLnvb+tHBiZ7O4EbYuKJoS/F40iZ4vfRp5+q\ngb0YJ8ayrdvCdYMeUFMcOz/hSQKBgQDHadDG5ZJMbRbHnPmJcfwpKKaCgOofSWWG\n+yo50va9aMWCdaqSZJOHtsRpFBVGwAqVQdOy/uZQDT0i4egcfvIIrR2w1cfFecld\n1W/iGFQ5h2YahbKTlfe4JSIXf60N5pQKkXJC7SBXwELtQ1AaUf2TLzVzNstMHLR1\n8TRPepMNSwKBgH8ZoRhB6F2TiyI09TAiIJwOuaxCrKv5EfYBRz+1S7+WCeKjaILx\nhuSLB7gy+qhsKM4nmnzZ2qyvTCXIGMGOhE4LPX4fTeUtkC/8CipOdUKSJ4aAt9Xk\nkW74OsLDIprEGBRC31TIpTVRt8t8gfwa+J/fiNljxr+JDVdqmBPCG5oZAoGAH3ik\nuW8ryqIA0VoFy9pQaJKAzOHZkTx9KHNlM6EGzdfGLBOz6syyt91xXAAOZ48RXIL6\nDSrLYGDmgCXVAwJJ4nKn1+u1ToYs8IEp2i3qxPWIeLEXANHPOaGqorjEsAfu30gb\nF1LjItY1+coAz1aXRW5S6i8AoK97D44UqmJ26McCgYBTaE5//SXMvPHzo3HNNdDJ\n7Vms/ng3aRrnHLpsQdlbcKM5Lfs9EpmLs83kxQhfEU5Wib2Afzd3EuLI2N79WYnC\nfpQKz6zNic/aTjQkh4WhhHNmSIlTF5yC4KV0yE4jM+ZfcHaA6iOyX8xYpxRjVI4M\nI6zqq76cdYHVNEFdZkMbbQ==\n-----END PRIVATE KEY-----\n",
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

