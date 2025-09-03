import logging
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable not set!")

# Command handler: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! 👋 Your bot is running successfully on Render.")

# Main entry point
async def main():
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command
    application.add_handler(CommandHandler("start", start))

    # Run the bot until Ctrl+C
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
