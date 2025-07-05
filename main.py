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

def main() -> None:
    """Start the bot."""
    LOGGER.info("🚀 Starting MovieKotha Bot...")

    # Set up the database (e.g., create indexes)
    setup_database()

    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # --- Register Handlers ---
    # Core handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_handler))
    
    # Admin handlers
    admin_handlers = [
        CommandHandler("add", add_movie_handler),
        CommandHandler("delete", delete_movie_handler),
        CommandHandler("list", list_movies_handler),
    ]
    application.add_handlers(admin_handlers)

    # --- Start the Bot ---
    LOGGER.info("✅ Bot has started and is now polling for updates.")
    application.run_polling()
    LOGGER.info("👋 Bot has been stopped.")

if __name__ == "__main__":
    main()