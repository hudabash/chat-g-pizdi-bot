import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
from openai import OpenAI

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = "https://chat-g-pizdi-bot.onrender.com"

client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(level=logging.INFO)

MODES = {
    "victor": {
        "name": "🧠 Виктор",
        "value": "Отвечай в стиле Виктора Равдайва: грубо, матом, без лести, с философией и харизмой. Глупости — говно, говори прямо."
    },
    "drunk": {
        "name": "🍷 Пьяный мудрец",
        "value": "Ты пьяный философ. Медленно, метафорично, сбивчиво. Иногда бред, но с глубоким подтекстом."
    },
    "gopnik": {
        "name": "🥶 Гопник-философ",
        "value": "Ты гопник с философским уклоном. Грубый, уличный, но с мудростью и цитатами великих."
    }
}

current_mode_key = "victor"

async def set_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_mode_key
    if context.args and context.args[0] in MODES:
        current_mode_key = context.args[0]
        await update.message.reply_text(f"✅ Режим изменён на: {MODES[current_mode_key]['name']}")
    else:
        mode_list = "\n".join([f"/mode {k} — {v['name']}" for k, v in MODES.items()])
        await update.message.reply_text(f"Выбери режим общения:\n{mode_list}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": MODES[current_mode_key]["value"]},
            {"role": "user", "content": user_message}
        ],
        temperature=0.95
    )

    await update.message.reply_text(response.choices[0].message.content.strip())

# 🚀 Запуск напрямую
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("mode", set_mode))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_webhook(
    listen="0.0.0.0",
    port=int(os.environ.get("PORT", 10000)),
    webhook_url=f"{WEBHOOK_URL}/webhook"
)
