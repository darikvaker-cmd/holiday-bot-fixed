import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ==========================
# НАСТРОЙКИ
# ==========================
BOT_TOKEN = "ТУТ_ТВОЙ_ТОКЕН"
ADMIN_ID = 8208653042
DB_FILE = "users.json"

# ==========================
# ЛОГИ
# ==========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==========================
# ФУНКЦИИ БАЗЫ
# ==========================
def load_db():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ==========================
# КОМАНДЫ
# ==========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Напиши, пожалуйста, своё имя:"
    )
    context.user_data["awaiting_name"] = True


async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_name"):
        return

    name = update.message.text.strip()
    context.user_data["name"] = name
    context.user_data["awaiting_name"] = False

    keyboard = [
        [
            InlineKeyboardButton("Приду", callback_data="yes"),
            InlineKeyboardButton("Не приду", callback_data="no")
        ]
    ]

    await update.message.reply_text(
        f"Имя записано: {name}\nТеперь выбери:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    name = context.user_data.get("name")
    if not name:
        await query.edit_message_text("Ошибка: имя не найдено. Напиши /start")
        return

    db = load_db()
    db[name] = "Приду" if query.data == "yes" else "Не приду"
    save_db(db)
