# bot.py
import os
import logging
import asyncio
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler, CallbackQueryHandler
)
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown

# Import custom modules
import tmdb
import gplink
import database

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
GP_API_KEY = os.getenv("GP_API_KEY")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", 0))

# --- Logging Setup ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# --- Conversation States for Admin Panel ---
(AWAIT_TMDB_ID, AWAIT_480P, AWAIT_720P, AWAIT_1080P, AWAIT_X265, AWAIT_CONFIRM) = range(6)

# --- Bot Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message."""
    user = update.effective_user
    welcome_message = (
        f"👋 *Welcome to MOVIEKOTHA, {escape_markdown(user.first_name, version=2)}*\\!\n\n"
        "I can help you find movie download links\\. Just send me a movie name to get started\\.\n\n"
        "🎬 **How to use me:**\n"
        "Simply type the name of the movie you're looking for \\(e\\.g\\., `Avatar`\\)\\."
    )
    if user.id == ADMIN_USER_ID:
        welcome_message += "\n\n*Admin Panel:*\n/addmovie \\- Start adding a new movie\\."
    await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN_V2)

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles user messages to search for movies."""
    query = update.message.text.strip()
    if len(query) < 3:
        await update.message.reply_text("⚠️ Please enter at least 3 characters to search.")
        return

    await update.message.reply_text(f"Searching for '{query}'... 🕵️‍♂️")
    found_movies = database.search_movies(query)

    if not found_movies:
        await update.message.reply_text(f"😞 Sorry, no movies found matching '{query}'. Please try another name.")
        return

    await update.message.reply_text(f"✅ Found {len(found_movies)} match(es)! Fetching details...")
    
    for movie_data in found_movies:
        # The data is now from our DB, fetch fresh TMDB details
        details = tmdb.get_movie_details(TMDB_API_KEY, movie_data.get("tmdb_id"))
        if not details:
            details = {"title": movie_data.get('title', 'N/A'), "overview": "N/A", "release_date": "N/A", "poster_url": None}

        buttons = []
        qualities = {"480p": "link_480p", "720p": "link_720p", "1080p": "link_1080p", "x265": "link_x265"}
        for quality_name, db_column in qualities.items():
            link = movie_data.get(db_column)
            if link:
                short_link = gplink.shorten_url(GP_API_KEY, link)
                buttons.append(InlineKeyboardButton(text=f"📥 {quality_name}", url=short_link))
        
        keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
        reply_markup = InlineKeyboardMarkup(keyboard)

        safe_title = escape_markdown(details["title"], version=2)
        safe_overview = escape_markdown(details["overview"], version=2)
        safe_release_date = escape_markdown(details["release_date"], version=2)
        safe_short_desc = escape_markdown(movie_data.get("short_description", ""), version=2)

        caption = (
            f"🎬 *{safe_title}*\n\n"
            f"📝 *Description*: {safe_short_desc}\n\n"
            f"🎞️ *Overview*: {safe_overview}\n\n"
            f"📆 *Release Date*: {safe_release_date}\n\n"
            f"👇 *Download Links* 👇"
        )
        
        try:
            if details["poster_url"]:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=details["poster_url"], caption=caption, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=reply_markup)
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=caption, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Failed to send movie message for '{details['title']}': {e}")
        await asyncio.sleep(1)

# --- Admin Panel Conversation ---

async def add_movie_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the conversation to add a new movie. Admin only."""
    if update.effective_user.id != ADMIN_USER_ID:
        return ConversationHandler.END
    await update.message.reply_text("🎬 **Add New Movie**\nPlease send me the TMDB ID of the movie. You can find it on the TMDB website URL (e.g., .../movie/157336-interstellar).")
    return AWAIT_TMDB_ID

async def process_tmdb_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes the TMDB ID and asks for the first link."""
    try:
        tmdb_id = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("⚠️ Invalid ID. Please send a numeric TMDB ID.")
        return AWAIT_TMDB_ID
    
    if database.check_movie_exists(tmdb_id):
        await update.message.reply_text("⚠️ This movie already exists in the database. Use /editmovie (not implemented) or delete it first.")
        return ConversationHandler.END

    details = tmdb.get_movie_details(TMDB_API_KEY, tmdb_id)
    if not details:
        await update.message.reply_text("⚠️ Could not find a movie with that TMDB ID. Please check the ID and try again.")
        return AWAIT_TMDB_ID

    context.user_data['new_movie'] = {
        'tmdb_id': tmdb_id,
        'title': details['title'],
        'short_description': details['overview'][:250] + '...' if len(details['overview']) > 250 else details['overview']
    }
    await update.message.reply_text(f"✅ Found: **{details['title']}**\n\nNow, send me the download link for **480p**. Type 'skip' if you don't have this link.")
    return AWAIT_480P

async def process_link(update: Update, context: ContextTypes.DEFAULT_TYPE, next_state: int, quality_name: str, next_quality_name: str):
    """Generic function to process a link and move to the next state."""
    link = update.message.text.strip()
    context.user_data['new_movie'][f'link_{quality_name}'] = None if link.lower() == 'skip' else link
    
    if next_state is None:
        # Last link, move to confirmation
        movie = context.user_data['new_movie']
        summary = (
            f"**Review Movie Details**\n\n"
            f"**Title**: {movie['title']}\n"
            f"**TMDB ID**: {movie['tmdb_id']}\n"
            f"**480p**: {movie.get('link_480p', 'N/A')}\n"
            f"**720p**: {movie.get('link_720p', 'N/A')}\n"
            f"**1080p**: {movie.get('link_1080p', 'N/A')}\n"
            f"**x265**: {movie.get('link_x265', 'N/A')}\n\n"
            "Is this correct?"
        )
        keyboard = [[InlineKeyboardButton("✅ Confirm & Save", callback_data="confirm_save"), InlineKeyboardButton("❌ Cancel", callback_data="cancel_save")]]
        await update.message.reply_text(summary, reply_markup=InlineKeyboardMarkup(keyboard))
        return AWAIT_CONFIRM
    else:
        await update.message.reply_text(f"Got it. Now send the link for **{next_quality_name}**. Type 'skip' to omit.")
        return next_state

async def receive_480p(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await process_link(update, context, AWAIT_720P, "480p", "720p")

async def receive_720p(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await process_link(update, context, AWAIT_1080P, "720p", "1080p")

async def receive_1080p(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await process_link(update, context, AWAIT_X265, "1080p", "x265")

async def receive_x265(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await process_link(update, context, None, "x265", "") # None indicates last state

async def confirm_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Saves the movie to the database after admin confirmation."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "confirm_save":
        movie_data = context.user_data.get('new_movie')
        if database.add_movie(movie_data):
            await query.edit_message_text("✅ Success! The movie has been added to the database.")
        else:
            await query.edit_message_text("❌ Error! There was a problem saving the movie to the database.")
    else:
        await query.edit_message_text("Operation cancelled.")
        
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels the current operation."""
    await update.message.reply_text("Operation cancelled.")
    context.user_data.clear()
    return ConversationHandler.END

def main():
    """Start the bot."""
    # Run the database initializer once at startup
    database.initialize_database()

    application = Application.builder().token(BOT_TOKEN).build()

    # Conversation handler for adding movies
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("addmovie", add_movie_start)],
        states={
            AWAIT_TMDB_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_tmdb_id)],
            AWAIT_480P: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_480p)],
            AWAIT_720P: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_720p)],
            AWAIT_1080P: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_1080p)],
            AWAIT_X265: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_x265)],
            AWAIT_CONFIRM: [CallbackQueryHandler(confirm_save)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search))

    logger.info("Bot is starting with MySQL backend...")
    application.run_polling()

if __name__ == "__main__":
    main()