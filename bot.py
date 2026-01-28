import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")

QUIZ_STORE = {}   # quiz_id : answer_key

# 1️⃣ Admin quiz forward kare
async def save_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.poll:
        poll = update.message.poll
        quiz_id = poll.id
        answers = [str(i+1) for i, opt in enumerate(poll.options) if opt.voter_count >= 0]

        # NOTE: Correct option Telegram already knows, admin manually set karega key
        QUIZ_STORE[quiz_id] = None

        await update.message.reply_text(
            "✅ Quiz saved!\n"
            "Ab /setkey 2,1,3,4 jaise answer key set karo"
        )

# 2️⃣ Answer key set kare
async def setkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ /setkey 2,1,3,4")
        return

    key = context.args[0].split(",")
    last_quiz = list(QUIZ_STORE.keys())[-1]
    QUIZ_STORE[last_quiz] = key

    await update.message.reply_text("📝 Answer key set ho gayi")

# 3️⃣ Group me quiz bheje
async def neetquiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not QUIZ_STORE:
        await update.message.reply_text("❌ Koi quiz saved nahi hai")
        return

    quiz_id = list(QUIZ_STORE.keys())[-1]
    await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        poll=quiz_id
    )

# 4️⃣ Score calculate kare
async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ /score 2,1,3,4")
        return

    user_ans = context.args[0].split(",")
    key = list(QUIZ_STORE.values())[-1]

    correct = wrong = 0
    for u, k in zip(user_ans, key):
        if u == k:
            correct += 1
        else:
            wrong += 1

    marks = correct * 4 - wrong

    await update.message.reply_text(
        f"📊 NEET RESULT\n\n"
        f"✅ Correct: {correct}\n"
        f"❌ Wrong: {wrong}\n"
        f"🎯 Marks: {marks}"
    )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.POLL, save_quiz))
app.add_handler(CommandHandler("setkey", setkey))
app.add_handler(CommandHandler("neetquiz", neetquiz))
app.add_handler(CommandHandler("score", score))
app.run_polling()
