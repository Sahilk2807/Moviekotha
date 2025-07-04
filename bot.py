# =================================================================
#                 FINAL bot.py FOR RENDER DEPLOYMENT
# =================================================================
import logging
import os
import asyncio
from dotenv import load_dotenv

# Import Flask and the request object
from flask import Flask, request

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# Make sure these files exist and are correct
import tmdb
import database
import gplink

# Load environment variables
load_dotenv()

# --- Get All Your Secrets from Render's Environment Variables ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USER_ID_STR = os.getenv("ADMIN_USER_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# --- Basic Setup and Logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# --- Important Check: Make sure all secrets are loaded ---
if not BOT_TOKEN:
    logger.critical("FATAL ERROR: BOT_TOKEN is not set!")
if not ADMIN_USER_ID_STR:
    logger.critical("FATAL ERROR: ADMIN_USER_ID is not set!")
if not WEBHOOK_URL:
    logger.critical("FATAL ERROR: WEBHOOK_URL is not set!")

# Convert ADMIN_USER_ID to an integer safely
try:
    ADMIN_USER_ID = int(ADMIN_USER_ID_STR)
except (ValueError, TypeError):
    logger.critical("FATAL ERROR: ADMIN_USER_ID is not a valid number!")
    ADMIN_USER_ID = None # Set to None to prevent crashes

# =================================================================
#                 YOUR BOT'S COMMAND HANDLERS
#          (These are your functions, no changes needed)
# =================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_message = (
        f"👋 Welcome to **MOVIEKOTHA**, {user.first_name}!\n\n"
        "I can help you find movie download links. Just send me a movie name (at least 3 characters) and I'll search for it.\n\n"
        "Use /help to see all available commands."
    )
    await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def add_movie_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ Sorry, this is an admin-only command.")
        return
    try:
        parts = " ".join(context.args).split(' | ')
        if len(parts) != 6:
            await update.message.reply_text(
                "❌ Incorrect format. Please use:\n"
                "/addmovie TMDB_ID | Title | 480p_link | 720p_link | 1080p_link | x265_link\n\n"
                "*Remember to use 'na' for any missing links.*"
            )
            return
        tmdb_id_str, title, link_480p, link_720p, link_1080p, link_x265 = parts
        tmdb_id = int(tmdb_id_str.strip())
        title = title.strip()
        links = {
            '480p': None if link_480p.strip().lower() == 'na' else link_480p.strip(),
            '720p': None if link_720p.strip().lower() == 'na' else link_720p.strip(),
            '1080p': None if link_1080p.strip().lower() == 'na' else link_1080p.strip(),
            'x265': None if link_x265.strip().lower() == 'na' else link_x265.strip(),
        }
        success, message = database.add_movie(title, tmdb_id, links)
        if success:
            await update.message.reply_text(f"✅ {message}")
        else:
            await update.message.reply_text(f"FAILED: {message}")
    except Exception as e:
        logger.error(f"Error in /addmovie command: {e}")
        await update.message.reply_text(f"An unexpected error occurred: {e}")

async def handle_movie_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    if len(query) < 3:
        return
    await update.message.reply_text(f"Searching for movies matching '{query}'...")
    movies = database.search_movies(query)
    if not movies:
        await update.message.reply_text(f"😞 Sorry, no movies found for '{query}'.")
        return
    await update.message.reply_text(f"Found {len(movies)} result(s)! Sending them now...")
    for movie_data in movies:
        tmdb_id = movie_data.get('tmdb_id')
        details = tmdb.get_movie_details(tmdb_id)
        if not details:
            continue
        caption_lines = [f"🎬 **{details['title']}**", f"📅 **Release Date:** {details['release_date']}\n", f"📝 **Overview:**\n{details.get('overview', 'N/A')}\n", "--- DOWNLOAD LINKS ---"]
        links = {"480p": movie_data.get('link_480p'), "720p": movie_data.get('link_720p'), "1080p": movie_data.get('link_1080p'), "x265": movie_data.get('link_x265')}
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
        try:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=details['poster_url'], caption=final_caption, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Failed to send photo for movie {details['title']}: {e}")
            await update.message.reply_text(f"Could not send poster for {details['title']}.\n\n{final_caption}", parse_mode=ParseMode.MARKDOWN)


# =================================================================
#        THE PART THAT RUNS ON RENDER (THE WEB SERVER)
# =================================================================

# Create the main application object
application = Application.builder().token(BOT_TOKEN).build()

# Add all the handlers from above
application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("addmovie", add_movie_command))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_movie_search))

# This is the small web server machine inside your bot.py file
# Gunicorn will find this 'app' object.
app = Flask(__name__)

# This is the webhook that Telegram sends updates to
@app.route("/webhook", methods=["POST"])
async def webhook():
    update = Update.de_json(await request.get_json(), application.bot)
    await application.process_update(update)
    return "OK"

# This is the homepage that the uptime monitor will ping
@app.route("/")
def index():
    return "Bot is alive!"

# This function runs only once when the server starts
async def setup():
    webhook_url = f"{WEBHOOK_URL}/webhook"
    await application.bot.set_webhook(url=webhook_url)
    logger.info(f"Webhook has been set to {webhook_url}")

# This makes sure the setup function runs when the server starts
# It runs the async function in a blocking way, just once.
asyncio.run(setup())