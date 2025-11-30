import os
import json
import logging
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ------------------- ЛОГИ -------------------
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ------------------- ПЕРЕМЕННЫЕ -------------------
BOT_TOKEN = "8214297458:AAEKUVeuKAHREcxOiGNFRPYj7K59uK4INYc"
ADMIN_ID = 8208653042
DB_FILE = "participants.json"

# ------------------- УДАЛЕНИЕ WEBHOOK -------------------
bot = Bot(token=BOT_TOKEN)
bot.delete_webhook()

# ------------------- ЗАГРУЗКА БД -------------------
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r", encoding="utf-8") as f:
        db = json.load(f)
else:
    db = []

# ------------------- HTTP-сервер для фейкового порта -------------------
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!\n")

def run_server():
    port = int(os.environ.get("PORT", 8000))  # Render подставляет PORT
    server = HTTPServer(("", port), SimpleHandler)
    print(f"Фейковий порт відкрито: {port}")
    server.serve_forever()

Thread(target=run_server, daemon=True).start()

# ------------------- ХЭНДЛЕРЫ -------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🎉 Прийду", "❌ Не прийду"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привіт! 😊\nВведи своє ім'я, а потім обери свій варіант 🎄👇",
        reply_markup=markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text in ["🎉 Прийду", "❌ Не прийду"]:
        if "name" in context.user_data:
            db.append(context.user_data["name"])
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(db, f, ensure_ascii=False, indent=2)
            await update.message.reply_text(
                f"Супер! 🎅 {context.user_data['name']} додано до списку гостей 🎁",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text("Спочатку введи своє ім'я 😉")
        return
    context.user_data["name"] = text
    await update.message.reply_text("Чудово! 🎄 Тепер обери свій варіант 👇")

# ------------------- АДМИН КОМАНДЫ -------------------
async def list_participants(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ У тебе немає доступу до цієї команди!")
        return
    if db:
        names = "\n".join(db)
        await update.message.reply_text(f"Список учасників:\n{names}")
    else:
        await update.message.reply_text("Список учасників поки що порожній.")

async def clear_participants(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ У тебе немає доступу до цієї команди!")
        return
    db.clear()
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    await update.message.reply_text("Список учасників очищено 🗑️")

# ------------------- ЗАПУСК -------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_participants))
    app.add_handler(CommandHandler("clear", clear_participants))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущено! 🎄✨🎅")
    app.run_polling()

if __name__ == "__main__":
    main()
