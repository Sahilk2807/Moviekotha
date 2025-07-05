# /moviekotha/main.py

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)
from config import BOT_TOKEN, LOGGER
from database import setup_database
from handlers.start import start
from handlers.admin import add_movie_handler, delete_movie_handler, list_movies_handler
from handlers.search import search_handler

def main():
    """Sets up and runs the Telegram bot."""
    LOGGER.info("🚀 Starting MovieKotha Bot...")

    # --- Step 1: Set up the database ---
    # This is a critical step. If the MONGO_DB_URL is wrong, it will fail here.
    try:
        setup_database()
        LOGGER.info("✅ Database setup successful.")
    except Exception as e:
        # If the database connection fails, log the error and stop the bot.
        LOGGER.error(f"❌ CRITICAL: Failed to setup database. The bot will not start. Error: {e}")
        return  # Exit the function

    # --- Step 2: Create the Telegram Bot Application ---
    try:
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        LOGGER.info("✅ Telegram Application built successfully.")
    except Exception as e:
        LOGGER.error(f"❌ CRITICAL: Failed to build Telegram application. Is the BOT_TOKEN valid? Error: {e}")
        return # Exit the function

    # --- Step 3: Register all command and message handlers ---
    # Command handlers react to commands like /start, /add
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_movie_handler))
    application.add_handler(CommandHandler("delete", delete_movie_handler))
    application.add_handler(CommandHandler("list", list_movies_handler))
    
    # Message handler for regular text messages (for searching movies)
    # This should generally be added last as it acts as a "catch-all" for non-command text.
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_handler))
    
    LOGGER.info("✅ All handlers have been registered.")

    # --- Step 4: Start the bot ---
    # run_polling() starts fetching updates from Telegram. This is a blocking call.
    LOGGER.info("⏳ Bot is now polling for updates...")
    application.run_polling()
    
    # This line will only be reached if the bot is stopped (e.g., with Ctrl+C)
    LOGGER.info("👋 Bot has been stopped.")

if __name__ == "__main__":
    main()