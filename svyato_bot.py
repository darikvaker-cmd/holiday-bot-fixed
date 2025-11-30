# svyato_bot.py
import os
import csv
import logging
from datetime import datetime
from threading import Lock

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# ---------------- Настройки ----------------
# Рекомендую задать BOT_TOKEN и ADMIN_ID через переменные окружения (Render -> Environment)
BOT_TOKEN = os.getenv("BOT_TOKEN", "")  # Вставь токен сюда или в ENV
ADMIN_ID = int(os.getenv("ADMIN_ID", "8208653042"))  # по умолчанию твой ID, можно переопределить
DATA_FILE = "guests.csv"  # файл, где храним имена и статусы
# -------------------------------------------

# Conversation states
NAME = 0
CONFIRM = 1

# Логи
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Файловая блокировка для потокобезопасности
file_lock = Lock()

def ensure_data_file():
    """Создаёт CSV с заголовком, если файла нет."""
    if not os.path.exists(DATA_FILE):
        with file_lock:
            with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["name", "status", "user_id", "timestamp"])

def append_guest(name: str, status: str, user_id: int):
    ensure_data_file()
    ts = datetime.utcnow().isoformat()
    with file_lock:
        with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([name, status, user_id, ts])

def read_all_guests():
    ensure_data_file()
    with file_lock:
        with open(DATA_FILE, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
    # rows[0] — header
    return rows

def remove_guest_by_name(name: str):
    ensure_data_file()
    updated = []
    removed = 0
    with file_lock:
        with open(DATA_FILE, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        header, data = rows[0], rows[1:]
        new_data = [r for r in data if r[0].strip().lower() != name.strip().lower()]
        removed = len(data) - len(new_data)
        updated_rows = [header] + new_data
        with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(updated_rows)
    return removed

# ---------------- Handlers ----------------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! 👋\nНапиши, будь ласка, своє ім'я (тільки ім'я), і потім вибери кнопку «Прийду» або «Не прийду».",
    )
    return NAME

async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if not name:
        await update.message.reply_text("Ім'я не може бути пустим. Введи, будь ласка, своє ім'я.")
        return NAME
    # Сохраняем временно имя в контексте пользователя
    context.user_data["given_name"] = name
    keyboard = [["🎉 Прийду", "❌ Не прийду"], ["/cancel"]]
    await update.message.reply_text(
        f"Дякую, {name}! Тепер обери, будь ласка:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return CONFIRM

async def receive_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.strip()
    name = context.user_data.get("given_name")
    if not name:
        await update.message.reply_text("Спочатку введи своє ім'я командою /start.")
        return ConversationHandler.END

    if choice in ["🎉 Прийду", "Прийду", "pryydu", "yes"]:
        status = "Прийду"
    elif choice in ["❌ Не прийду", "Не прийду", "no"]:
        status = "Не прийду"
    else:
        await update.message.reply_text("Будь ласка, обери одну з кнопок.")
        return CONFIRM

    append_guest(name, status, update.effective_user.id)
    await update.message.reply_text(f"Дякую, {name}! Твій вибір «{status}» збережено. 🎄", reply_markup=ReplyKeyboardRemove())
    context.user_data.pop("given_name", None)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("given_name", None)
    await update.message.reply_text("Скасовано.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# ----- Admin commands -----

def is_admin(user_id: int):
    return user_id == ADMIN_ID

async def cmd_guests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ Ця команда доступна лише адміну.")
        return
    rows = read_all_guests()
    if len(rows) <= 1:
        await update.message.reply_text("Поки що ніхто не зареєструвався.")
        return
    # build message
    lines = []
    for r in rows[1:]:
        name, status, uid, ts = r
        lines.append(f"{name} — {status}")
    text = "📋 Список гостей:\n" + "\n".join(lines)
    # Telegram message length limit ~4096, chunk if needed
    for i in range(0, len(text), 3900):
        await update.message.reply_text(text[i:i+3900])

async def cmd_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ Тільки адміністратор.")
        return
    rows = read_all_guests()
    count = max(0, len(rows) - 1)
    await update.message.reply_text(f"Зареєстровано гостей: {count}")

async def cmd_export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ Тільки адміністратор.")
        return
    ensure_data_file()
    # send file
    await update.message.reply_document(open(DATA_FILE, "rb"))

async def cmd_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ Тільки адміністратор.")
        return
    args = context.args
    if not args:
        await update.message.reply_text("Використання: /remove Ім'я  — видалить всі записи з цим ім'ям")
        return
    name = " ".join(args)
    removed = remove_guest_by_name(name)
    await update.message.reply_text(f"Видалено записів з ім'ям '{name}': {removed}")

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Доступні команди:\n"
        "/start — почати (ввести ім'я і вибрати Прийду/Не прийду)\n"
        "/cancel — скасувати поточну дію\n"
        "\n"
        "Адмін-команди (тільки для адміністратора):\n"
        "/guests — показати список гостей\n"
        "/count — показати кількість зареєстрованих\n"
        "/export — завантажити CSV-файл зі свята\n"
        "/remove Ім'я — видалити записи з цим ім'ям\n"
        "/help — показати цю довідку\n"
    )
    await update.message.reply_text(text)

# ---------------- Main ----------------
def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не задан. Встанови змінну оточення BOT_TOKEN або встав токен в код.")
        raise SystemExit("BOT_TOKEN required")

    ensure_data_file()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", cmd_start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("guests", cmd_guests))
    app.add_handler(CommandHandler("count", cmd_count))
    app.add_handler(CommandHandler("export", cmd_export))
    app.add_handler(CommandHandler("remove", cmd_remove))
    app.add_handler(CommandHandler("help", cmd_help))

    logger.info("Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()

