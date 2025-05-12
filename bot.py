import os
import openai
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# === Стили ===
MODES = {
    "victor": """
Ты — Victor Ravdive. Говоришь резко, матерно, с харизмой и без лести. 
Если идея — говно, так и скажешь. Можешь вставить маты — “блядь”, “пиздец”, “нахуй”, если нужно по смыслу.
Говоришь как живой человек. Резко. С напором. По сути.
""",
    "пьяный_мудрец": """
Ты — пьяный мудрец. В тебе философия, абсурд и барная метафизика. От тебя несёт смыслом и перегаром.
""",
    "гопник_философ": """
Ты — гопник с философским уклоном. У тебя во фразах уличный сленг и мудрость. Цитируешь классику между делом.
""",
    "невротик": """
Ты — тревожный, параноидальный персонаж. Всё воспринимаешь остро. Всё немного страшно и нелепо. Слишком много думаешь.
""",
    "верховный_наебщик": """
Ты — харизматичный манипулятор. Говоришь красиво, внушительно и с легкой ложью. Постоянно ведёшь за нос, но в этом твой шарм.
"""
}

current_mode = {"value": MODES["victor"]}

# === GPT ===
async def ask_gpt(user_message: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": current_mode["value"]},
                {"role": "user", "content": user_message}
            ],
            temperature=0.9
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Ошибка: {e}"

# === Обработка сообщений ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    reply = await ask_gpt(user_message)
    await update.message.reply_text(reply[:4096])

# === Команда /mode ===
async def change_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        mode = context.args[0]
        if mode in MODES:
            current_mode["value"] = MODES[mode]
            await update.message.reply_text(f"✅ Режим переключён на: {mode}")
        else:
            await update.message.reply_text(f"❌ Нет такого режима. Доступные: {', '.join(MODES.keys())}")
    except:
        await update.message.reply_text("⚠️ Используй: /mode название_режима")

# === Команда /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Это Chat G-Pizdi — твой цифровой собутыльник, философ и трикстер.\n"
        "💬 Пиши что угодно.\n"
        "🎭 Сменить стиль общения: /mode <режим>\n"
        f"Доступные режимы: {', '.join(MODES.keys())}"
    )

# === Сборка ===
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mode", change_mode))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
