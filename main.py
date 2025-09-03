import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from scraper import BookMyShowScraper

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Env vars (set these in Render dashboard)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # your Telegram user/chat ID

# Movie URL to monitor
MOVIE_URL = "https://in.bookmyshow.com/mumbai/movies/some-movie"

scraper = BookMyShowScraper()

# === Telegram bot handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm monitoring tickets for you.")

# === Monitoring loop ===
async def monitor_tickets(application):
    while True:
        result = scraper.check_ticket_availability(MOVIE_URL)

        if result["available"]:
            msg = f"🎟 Tickets available for *{result['title']}*! \n{result['url']}"
            logger.info(msg)
            if CHAT_ID:
                await application.bot.send_message(
                    chat_id=CHAT_ID,
                    text=msg,
                    parse_mode="Markdown"
                )
        else:
            logger.info(f"No tickets yet for {result['title']}: {result['status']}")

        await asyncio.sleep(60)  # check every 60 sec

# === Main entrypoint ===
async def main():
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set!")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    # /start handler
    application.add_handler(CommandHandler("start", start))

    # Start background monitoring task
    application.job_queue.run_repeating(
        lambda _: asyncio.create_task(monitor_tickets(application)),
        interval=60,
        first=5
    )

    logger.info("Bot started!")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
