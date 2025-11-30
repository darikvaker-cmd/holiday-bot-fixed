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
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("", port), SimpleHandler)
    print(f"Фейковий порт відкрито: {port}")
    server.serve_forever()

Thread(target=run_server, daemon=True).start()

# ------------------- ХЭНДЛЕРЫ -------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Ребенок", "Взрослый"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привіт! 😊\nВибери категорію учасника 🎄👇",
        reply_markup=markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # Выбор категории
    if text in ["Ребенок", "Взрослый"]:
        context.user_data["category"] = text
        keyboard = [["🎉 Прийду", "❌ Не прийду"]]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "Тепер введи своє ім'я 👇",
            reply_markup=markup
        )
        return

    # Ввод имени
    if "category" in context.user_data and text not in ["🎉 Прийду", "❌ Не прийду"]:
        context.user_data["name"] = text
        await update.message.reply_text(
            f"Чудово! 🎄 Тепер обери свій варіант 👇"
        )
        return

    # Прийду / Не прийду
    if text in ["🎉 Прийду", "❌ Не прийду"]:
        if "name" not in context.user_data or "category" not in context.user_data:
            await update.message.reply_text("Спочатку введи своє ім'я та обери категорію 😉")
            return
        db.append({
            "name": context.user_data["name"],
            "status": text,
            "category": context.user_data["category"]
        })
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)

        await update.message.reply_text(
            f"✅ {context.user_data['name']} ({context.user_data['category']}) додано до списку гостей 🎁",
            reply_markup=ReplyKeyboardRemove()
        )

        # Уведомление админа
        try:
            await bot.send_message(
                chat_id=ADMIN_ID,
                text=f"Новий учасник: {context.user_data['name']} ({context.user_data['category']}) — {text}"
            )
        except Exception as e:
            logger.warning(f"Не вдалося надіслати повідомлення адміну: {e}")

        context.user_data.clear()
        return

# ------------------- АДМИН КОМАНДЫ -------------------
async def list_participants(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ У тебе немає доступу до цієї команди!")
        return
    if db:
        msg = "\n".join([f"{p['name']} — {p['status']} — {p['category']}" for p in db])
        await update.message.reply_text(f"Список учасників:\n{msg}")
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

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("❌ У тебе немає доступу до цієї команди!")
        return
    total = len(db)
    kids = sum(1 for p in db if p["category"] == "Ребенок")
    adults = sum(1 for p in db if p["category"] == "Взрослый")
    await update.message.reply_text(f"📊 Статистика:\nВсього: {total}\nДіти: {kids}\nДорослі: {adults}")

# ------------------- ЗАПУСК -------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_participants))
    app.add_handler(CommandHandler("clear", clear_participants))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущено! 🎄✨🎅")
    app.run_polling()

if __name__ == "__main__":
    main()