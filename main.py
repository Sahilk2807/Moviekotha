# /moviekotha/main.py

import os
import threading
from flask import Flask
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

# --- Flask Web Server Setup (to keep Render's Web Service alive) ---
app = Flask(__name__)

@app.route('/')
def index():
    return "MovieKotha Bot is alive!"

def run_flask():
    # Render provides the PORT environment variable.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# --- Telegram Bot Setup ---
def run_telegram_bot():
    """Start the bot."""
    LOGGER.info("🚀 Starting MovieKotha Bot...")

    # Set up the database (e.g., create indexes)
    setup_database()

    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Register Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_handler))
    
    application.add_handler(CommandHandler("add", add_movie_handler))
    application.add_handler(CommandHandler("delete", delete_movie_handler))
    application.add_handler(CommandHandler("list", list_movies_handler))

    # Start the Bot
    LOGGER.info("✅ Bot has started and is now polling for updates.")
    application.run_polling()
    LOGGER.info("👋 Bot has been stopped.")

if __name__ == "__main__":
    # Run Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    # Run the Telegram bot in the main thread
    run_telegram_bot()