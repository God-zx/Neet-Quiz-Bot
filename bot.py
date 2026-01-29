import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# 🔐 TOKEN (Render ENV se)
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN not set")

# quiz data store
QUIZ_DATA = {
    "chat_id": None,
    "message_id": None,
    "answer_key": None
}

# 1️⃣ Admin quiz forward kare
async def save_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.poll:
        QUIZ_DATA["chat_id"] = update.message.chat_id
        QUIZ_DATA["message_id"] = update.message.message_id
        QUIZ_DATA["answer_key"] = None

        await update.message.reply_text(
            "✅ Quiz saved!\n"
            "Ab answer key set karo:\n"
            "/setkey 2,1,3,4"
        )

# 2️⃣ Answer key set kare
async def setkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Use: /setkey 2,1,3,4")
        return

    QUIZ_DATA["answer_key"] = context.args[0].split(",")
    await update.message.reply_text("📝 Answer key saved")

# 3️⃣ Group me quiz bheje
async def neetquiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not QUIZ_DATA["message_id"]:
        await update.message.reply_text("❌ Pehle quiz forward karo")
        return

    await context.bot.copy_message(
        chat_id=update.effective_chat.id,
        from_chat_id=QUIZ_DATA["chat_id"],
        message_id=QUIZ_DATA["message_id"]
    )

# 4️⃣ Score calculate kare (+4 / −1)
async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not QUIZ_DATA["answer_key"]:
        await update.message.reply_text("❌ Answer key set nahi hai")
        return

    if not context.args:
        await update.message.reply_text("❌ Use: /score 2,1,3,4")
        return

    user_ans = context.args[0].split(",")
    key = QUIZ_DATA["answer_key"]

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

# 🚀 App
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.POLL, save_quiz))
app.add_handler(CommandHandler("setkey", setkey))
app.add_handler(CommandHandler("neetquiz", neetquiz))
app.add_handler(CommandHandler("score", score))

app.run_polling()
