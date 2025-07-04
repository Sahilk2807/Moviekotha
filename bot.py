import logging
import os
from dotenv import load_dotenv

from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

import tmdb
import database
import gplink

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID"))

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message when the /start command is issued."""
    user = update.effective_user
    welcome_message = (
        f"👋 Welcome to **MOVIEKOTHA**, {user.first_name}!\n\n"
        "I can help you find movie download links. Just send me a movie name (at least 3 characters) and I'll search for it.\n\n"
        "Use /help to see all available commands."
    )
    await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a help message with instructions."""
    help_text = (
        "🎬 **How to use MOVIEKOTHA Bot** 🎬\n\n"
        "1️⃣ **Search for a Movie:**\n"
        "   - Simply type the name of the movie you want to find (e.g., `avatar`).\n"
        "   - The search is case-insensitive and needs at least 3 letters.\n\n"
        "2️⃣ **Commands:**\n"
        "   - /start - Show the welcome message.\n"
        "   - /help - Display this help message.\n\n"
        "Happy watching! 🍿"
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def reload_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin-only command to check database connection status."""
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("Sorry, this is an admin-only command.")
        return

    await update.message.reply_text("🔄 Checking database connection...")
    is_connected = database.check_db_connection()
    if is_connected:
        await update.message.reply_text("✅ Database connection is successful!")
    else:
        await update.message.reply_text("❌ Failed to connect to the database. Please check the logs.")


# --- Message Handler ---

async def handle_movie_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles user messages to search for movies."""
    query = update.message.text.strip()

    if len(query) < 3:
        await update.message.reply_text("⚠️ Please enter at least 3 characters to search.")
        return
    
    await update.message.reply_text(f"Searching for movies matching '{query}'...")

    # Search for movies in the database
    movies = database.search_movies(query)

    if not movies:
        await update.message.reply_text(f"😞 Sorry, no movies found for '{query}'. Please try another name.")
        return
        
    await update.message.reply_text(f"Found {len(movies)} result(s)! Sending them now...")

    for movie_data in movies:
        tmdb_id = movie_data.get('tmdb_id')
        
        # Get richer details from TMDB
        details = tmdb.get_movie_details(tmdb_id)
        if not details:
            logger.warning(f"Could not fetch TMDB details for ID: {tmdb_id}")
            continue

        # Build the message caption with download links
        caption_lines = [
            f"🎬 **{details['title']}**",
            f"📅 **Release Date:** {details['release_date']}\n",
            f"📝 **Overview:**\n{details.get('overview', 'N/A')}\n",
            "--- DOWNLOAD LINKS ---"
        ]
        
        # Create a dictionary for links to iterate over
        links = {
            "480p": movie_data.get('link_480p'),
            "720p": movie_data.get('link_720p'),
            "1080p": movie_data.get('link_1080p'),
            "x265": movie_data.get('link_x265'),
        }

        has_links = False
        for quality, url in links.items():
            if url and url.strip():
                short_url = gplink.shorten_url(url)
                if short_url:
                    caption_lines.append(f"🔗 **{quality.upper()}:** [Download]({short_url})")
                    has_links = True
        
        if not has_links:
            caption_lines.append("No download links available for this movie yet.")

        final_caption = "\n".join(caption_lines)

        # Send the poster with the caption
        try:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=details['poster_url'],
                caption=final_caption,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Failed to send photo for movie {details['title']}: {e}")
            await update.message.reply_text(f"Could not send poster for {details['title']}, but here are the details:\n\n{final_caption}", parse_mode=ParseMode.MARKDOWN)


# --- Main Bot Setup ---

def main():
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reload", reload_command))

    # Add message handler for movie search (filters for text and non-commands)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_movie_search))

    # Start the Bot
    logger.info("Starting bot...")
    application.run_polling()

if __name__ == "__main__":
    main()