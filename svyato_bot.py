import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ===============================
# НАСТРОЙКИ
# ===============================

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Вставишь в Render → Environment
ADMIN_ID = 8208653042

USERS_FILE = "users.json"

# ===============================
# ФУНКЦИИ ДЛЯ РАБОТЫ С ФАЙЛОМ
# ===============================

def load_users():
    """Загружает пользователей из файла."""
    if not os.path.exists(USERS_FILE):
        return []

    with open(USERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def save_users(users):
    """Сохраняет пользователей в файл."""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# ===============================
# КОМАНДЫ БОТА
# ===============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    users = load_users()

    if user.id not in users:
        users.append(user.id)
        save_users(users)

    await update.message.reply_text(
        f"🎄 Приветствую, {user.first_name}! Ты добавлен в список участников!"
    )


async def participants(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список участников. Только для админа."""
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("⛔ У тебя нет прав!")

    users = load_users()

    if not users:
        return await update.message.reply_text("Список пуст 😢")

    text = "🎅 *Список участников:*\n\n" + "\n".join([f"• `{uid}`" for uid in users])
    await update.message.reply_text(text, parse_mode="Markdown")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Заглушка — на все сообщения."""
    await update.message.reply_text("✨ Я тебя услышал!")


# ===============================
# ЗАПУСК БОТА
# ===============================

def main():
    if not BOT_TOKEN:
        raise ValueError("❌ ERROR: переменная BOT_TOKEN не задана! Добавь в Render.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("participants", participants))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
