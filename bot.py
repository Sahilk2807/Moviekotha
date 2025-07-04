# bot.py
import os
import logging
import json
import asyncio
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown

# Import custom modules
import tmdb
import gplink
from sheet import GoogleSheet

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
GP_API_KEY = os.getenv("GP_API_KEY")
SHEET_ID = os.getenv("SHEET_ID")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", 0))


# <<< THIS BLOCK IS THE FIX >>>
# It correctly parses the multi-line private key from the single-line .env variable.
# ----------------------------------------------------------------------------------
# Securely load Google Credentials from .env
try:
    GOOGLE_CREDENTIALS_JSON_STR = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not GOOGLE_CREDENTIALS_JSON_STR:
        raise ValueError("GOOGLE_CREDENTIALS_JSON environment variable not set.")
    
    # First, load the JSON string into a Python dictionary
    creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON_STR)
    
    # Then, fix the private_key by replacing the escaped newlines with actual newlines
    creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')
    
    # This is the final, corrected dictionary to be used by gspread
    GOOGLE_CREDENTIALS = creds_dict

except (json.JSONDecodeError, ValueError, KeyError) as e:
    logging.critical(f"FATAL: Could not load or parse Google credentials. Check .env. Error: {e}")
    exit()
# ----------------------------------------------------------------------------------


# --- Logging Setup ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# --- Bot Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message when the /start command is issued."""
    user = update.effective_user
    welcome_message = (
        f"👋 *Welcome to MOVIEKOTHA, {escape_markdown(user.first_name, version=2)}*\\!\n\n"
        "I can help you find movie download links\\. Just send me a movie name to get started\\.\n\n"
        "🎬 **How to use me:**\n"
        "Simply type the name of the movie you're looking for \\(e\\.g\\., `Avatar`\\)\\.\n\n"
        "For more help, use the /help command\\."
    )
    await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN_V2)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a help message with instructions."""
    help_text = (
        "🆘 *Help & Instructions*\n\n"
        "1\\. *Search for a Movie*:\n"
        "   \\- Send me a movie title \\(minimum 3 characters\\)\\.\n"
        "   \\- Example: `interstellar`\n\n"
        "2\\. *Get Links*:\n"
        "   \\- If the movie is found, I'll send you its details and a poster\\.\n"
        "   \\- Download links for different qualities will be available as buttons\\.\n\n"
        "3\\. *Commands*:\n"
        "   \\- /start \\- Show the welcome message\\.\n"
        "   \\- /help \\- Show this help message\\.\n"
        "   \\- /ping \\- Check if the bot is alive\\.\n\n"
        "Enjoy your movies\\! 🍿"
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN_V2)

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """A simple command to check if the bot is running."""
    await update.message.reply_text("Pong! 🏓 I'm alive and kicking.")

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles user messages to search for movies."""
    query = update.message.text.strip()

    if len(query) < 3:
        await update.message.reply_text("⚠️ Please enter at least 3 characters to search.")
        return

    await update.message.reply_text(f"Searching for '{query}'... 🕵️‍♂️")

    # Search Google Sheet
    sheet_client = context.bot_data["sheet_client"]
    found_movies = sheet_client.search_movies(query)

    if not found_movies:
        await update.message.reply_text(f"😞 Sorry, no movies found matching '{query}'. Please check the spelling or try another name.")
        return

    await update.message.reply_text(f"✅ Found {len(found_movies)} match(es)! Fetching details...")
    
    for movie_data in found_movies:
        tmdb_id = movie_data.get("TMDB_ID")
        if not tmdb_id:
            logger.warning(f"Skipping movie '{movie_data.get('Title')}' due to missing TMDB_ID.")
            continue

        # Fetch details from TMDB
        details = tmdb.get_movie_details(TMDB_API_KEY, tmdb_id)
        if not details:
            logger.warning(f"Could not fetch TMDB details for ID: {tmdb_id}")
            # Fallback to sheet data if TMDB fails
            details = {
                "title": movie_data.get('Title', 'N/A'),
                "overview": movie_data.get('Short Description', 'No overview available.'),
                "release_date": 'N/A',
                "poster_url": None
            }

        # Build download links and shorten them
        buttons = []
        qualities = ["480p", "720p", "1080p", "x265"]
        for quality in qualities:
            link = movie_data.get(quality)
            if link:
                short_link = gplink.shorten_url(GP_API_KEY, link)
                buttons.append(InlineKeyboardButton(text=f"📥 {quality}", url=short_link))
        
        # We need to arrange buttons in rows, max 3 per row
        keyboard = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Escape all user-generated content for MarkdownV2
        safe_title = escape_markdown(details["title"], version=2)
        safe_overview = escape_markdown(details["overview"], version=2)
        safe_release_date = escape_markdown(details["release_date"], version=2)
        safe_short_desc = escape_markdown(movie_data.get("Short Description", ""), version=2)

        # Format the caption
        caption = (
            f"🎬 *{safe_title}*\n\n"
            f"📝 *Description*: {safe_short_desc}\n\n"
            f"🎞️ *Overview*: {safe_overview}\n\n"
            f"📆 *Release Date*: {safe_release_date}\n\n"
            f"👇 *Download Links* 👇"
        )
        
        try:
            if details["poster_url"]:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=details["poster_url"],
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=reply_markup,
                )
            else:
                # Send text message if no poster is available
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=caption,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=reply_markup,
                )
        except Exception as e:
            logger.error(f"Failed to send movie message for '{details['title']}': {e}")
            await update.message.reply_text(f"An error occurred while sending details for {details['title']}.")
        
        await asyncio.sleep(1) # To avoid rate limiting


def main():
    """Start the bot."""
    if not all([BOT_TOKEN, TMDB_API_KEY, GP_API_KEY, SHEET_ID, ADMIN_USER_ID]):
        logging.critical("FATAL: One or more required environment variables are missing.")
        return

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # Initialize and store the Google Sheet client in bot_data
    try:
        # This now uses the corrected GOOGLE_CREDENTIALS dictionary
        sheet_client = GoogleSheet(credentials=GOOGLE_CREDENTIALS, sheet_id=SHEET_ID)
        application.bot_data["sheet_client"] = sheet_client
    except Exception as e:
        logging.critical(f"Could not start the bot due to Google Sheet initialization failure: {e}")
        return

    # --- Register Handlers ---
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping_command))
    
    # Message handler for movie searches
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search))

    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()