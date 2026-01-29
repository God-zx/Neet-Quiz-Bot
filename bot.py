import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# 🔐 Token from Render ENV
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN not set")

# Temporary in-memory storage
USERS = {}
QUIZZES = {}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ Create NEET Quiz", callback_data="create")],
        [InlineKeyboardButton("📚 My Quizzes", callback_data="myquizzes")],
    ]
    await update.message.reply_text(
        "🧠 *NEET Quiz Bot*\n\n"
        "Create NEET-style quizzes (+4 / −1)\n"
        "Just like @quizbot 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )

# Button handler
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id

    if query.data == "create":
        USERS[uid] = {"step": "question", "data": {}}
        await query.message.reply_text("📝 Send *Question*", parse_mode="Markdown")

    elif query.data == "myquizzes":
        if uid not in QUIZZES:
            await query.message.reply_text("❌ No quizzes yet")
        else:
            await query.message.reply_text("📚 Your quiz is ready. Use /share")

# Message handler (quiz creation flow)
async def collect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    if uid not in USERS:
        return

    step = USERS[uid]["step"]

    if step == "question":
        USERS[uid]["data"]["question"] = update.message.text
        USERS[uid]["step"] = "options"
        USERS[uid]["data"]["options"] = []
        await update.message.reply_text("Send option 1")

    elif step == "options":
        USERS[uid]["data"]["options"].append(update.message.text)
        count = len(USERS[uid]["data"]["options"])

        if count < 4:
            await update.message.reply_text(f"Send option {count+1}")
        else:
            USERS[uid]["step"] = "answer"
            await update.message.reply_text("✅ Send correct option number (1-4)")

    elif step == "answer":
        correct = int(update.message.text) - 1
        quiz = USERS[uid]["data"]

        QUIZZES[uid] = {
            "question": quiz["question"],
            "options": quiz["options"],
            "correct": correct,
        }

        del USERS[uid]
        await update.message.reply_text(
            "🎉 Quiz created!\n\nUse /share to send in group"
        )

# Share quiz
async def share(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    if uid not in QUIZZES:
        await update.message.reply_text("❌ No quiz found")
        return

    q = QUIZZES[uid]

    await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=q["question"],
        options=q["options"],
        type="quiz",
        correct_option_id=q["correct"],
        is_anonymous=False,
    )

# App
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("share", share))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect))

app.run_polling()
