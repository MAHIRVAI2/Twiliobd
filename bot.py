import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    ConversationHandler, MessageHandler, filters
)
from twilio.rest import Client

# Conversation states
LOGIN_SID, LOGIN_TOKEN = range(2)

# Dictionary to store logged-in Twilio clients per user
user_clients = {}

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ✅ /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 হ্যালো! Twilio Telegram Bot এ স্বাগতম!\n\n"
        "🔐 লগইন করতে /login লিখুন\n"
        "❌ বাতিল করতে /cancel লিখুন"
    )

# ✅ Step 1: Ask for SID
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛡️ আপনার Twilio Account SID দিন:")
    return LOGIN_SID

# ✅ Step 2: Save SID and ask for Token
async def get_sid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sid"] = update.message.text.strip()
    await update.message.reply_text("🔑 এখন আপনার Twilio Auth Token দিন:")
    return LOGIN_TOKEN

# ✅ Step 3: Save Token and validate login
async def get_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sid = context.user_data.get("sid")
    token = update.message.text.strip()
    user_id = update.message.from_user.id

    try:
        client = Client(sid, token)
        # Validate credentials
        client.api.accounts(sid).fetch()

        user_clients[user_id] = client
        await update.message.reply_text("✅ সফলভাবে লগইন হয়েছে! এখন আপনি কমান্ড ব্যবহার করতে পারবেন।")

    except Exception as e:
        logging.error(f"Login failed for user {user_id}: {e}")
        await update.message.reply_text("❌ লগইন ব্যর্থ! SID বা Token ভুল হতে পারে। আবার চেষ্টা করুন।")

    return ConversationHandler.END

# ✅ Cancel command to stop the login process
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ লগইন প্রক্রিয়া বাতিল করা হয়েছে।")
    return ConversationHandler.END

# ✅ Main function to run the bot
if __name__ == "__main__":
    import asyncio

    async def main():
        TOKEN = "7399378678:AAFN8Gvwjz_aEcASevD1p5MxSL6QKkh1pX0"  # <-- এখানে আপনার Bot Token বসান

        app = ApplicationBuilder().token(TOKEN).build()

        # Login conversation handler
        login_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("login", login)],
            states={
                LOGIN_SID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_sid)],
                LOGIN_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_token)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )

        # Handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(login_conv_handler)

        print("🤖 Bot is running...")
        await app.run_polling()

    asyncio.run(main())
