import json
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# ---------------------------
# НАСТРОЙКИ
# ---------------------------
BOT_TOKEN = "8214297458:AAEKUVeuKAHREcxOiGNFRPYj7K59uK4INYc"
ADMIN_ID = 8208653042

DB_FILE = "database.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------
# Загрузка / Сохранение БД
# ---------------------------
def load_db():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------------------------
# Состояния диалога
# ---------------------------
ASK_NAME, ASK_STATUS = range(2)


# ---------------------------
# Команды
# ---------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Напиши, будь ласка, своє ім’я:")
    return ASK_NAME


async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text.strip()

    keyboard = [["Прийду"], ["Не прийду"]]
    await update.message.reply_text(
        "Добре! Тепер обери варіант:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return ASK_STATUS


async def ask_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = update.message.text.strip()
    name = context.user_data["name"]

    db = load_db()
    db.append({"name": name, "status": status})
    save_db(db)

    await update.message.reply_text(
        f"Дякую, {name}! Я записав тебе як: {status}.",
        reply_markup=None
    )
    return ConversationHandler.END


# ---------------------------
# Админ-панель
# ---------------------------
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return await update.message.reply_text("⛔ У тебе немає прав!")

    await update.message.reply_text(
        "Адмін-меню:\n/list — список\n/clear — очистити базу"
    )


async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return await update.message.reply_text("⛔ Немає доступу!")

    db = load_db()
    if not db:
        return await update.message.reply_text("База порожня.")

    text = "Список учасників:\n\n"
    for user in db:
        text += f"{user['name']} — {user['status']}\n"

    await update.message.reply_text(text)


async def clear_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return await update.message.reply_text("⛔ Немає доступу!")

    save_db([])
    await update.message.reply_text("Базу очищено!")


# ---------------------------
# Запуск бота
# ---------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_STATUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_status)],
        },
        fallbacks=[],
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("list", list_users))
    app.add_handler(CommandHandler("clear", clear_db))

    app.run_polling()


if __name__ == "__main__":
    main()


