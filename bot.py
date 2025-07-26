from telegram.ext import ApplicationBuilder, CommandHandler
import logging
import os

TOKEN = os.getenv("TOKEN")  # Make sure your TOKEN is properly set in environment or define it here

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Sample start command
async def start(update, context):
    await update.message.reply_text('Bot is running!')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))

    # THIS replaces Updater usage:
    app.run_polling()
