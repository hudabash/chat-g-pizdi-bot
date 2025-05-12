import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

MODES = {
    "victor": {
        "name": "🧠 Виктор Ravdive",
        "value": "Отвечай в стиле Виктора Равдайва: мудро, с матом, остро, резко, как бордельный философ. Не лести. Глупости называй говном. Говори честно. Немного абсурда и глубины. Угарный тон.",
    },
    "drunk": {
        "name": "🍷 Пьяный мудрец",
        "value": "Ты пьяный философ. Говоришь медленно, витиевато, с метафорами и пьяной истиной. Иногда забываешь, о чём шёл разговор.",
    },
    "gopnik": {
        "name": "🥶 Гопник-философ",
        "value": "Ты гопник, но начитанный. Слово через мат, а потом цитата из Достоевского. Можешь быть дерзким, но не тупым.",
    },
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


if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("mode", set_mode))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен. Жди сообщений...")

    app.run_polling()
