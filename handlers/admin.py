# /moviekotha/handlers/admin.py

import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from config import ADMIN_ID
from database import add_movie, delete_movie, list_all_movies
from tmdb import search_movie_by_name
from gplink import shorten_url

LOGGER = logging.getLogger(__name__)

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

async def add_movie_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /add command. Format: /add <Movie Name> <quality>:<link> [quality2:link2]..."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔️ Sorry, this command is for admins only.")
        return

    args = context.args
    if not args:
        await update.message.reply_text("⚠️ **Invalid format.**\nUsage: `/add <Movie Name> <quality>:<link> ...`", parse_mode='Markdown')
        return

    link_args_start_index = -1
    for i, arg in enumerate(args):
        if ":" in arg and ("http://" in arg or "https://" in arg):
            link_args_start_index = i
            break

    if link_args_start_index == -1 or link_args_start_index == 0:
        await update.message.reply_text(
            "⚠️ **Invalid format.**\nProvide a movie name followed by at least one `quality:link` pair.\n\n"
            "**Example:** `/add The Matrix 1080p:http://example.com/movie.mkv`", parse_mode='Markdown'
        )
        return

    movie_name = " ".join(args[:link_args_start_index])
    link_pairs = args[link_args_start_index:]

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    msg = await update.message.reply_text(f"⏳ Fetching details for *{movie_name}*...", parse_mode='Markdown')

    # FIXED: Use await for the network call
    tmdb_data = await search_movie_by_name(movie_name)
    if not tmdb_data:
        await msg.edit_text(f"❌ **Movie not found!**\nCould not find '{movie_name}' on TMDb. Please check spelling.", parse_mode='Markdown')
        return

    await msg.edit_text("🔗 Shortening download links...")

    download_links = []
    for pair in link_pairs:
        try:
            quality, original_link = pair.split(":", 1)
            if not original_link.startswith(('http://', 'https://')): raise ValueError("Invalid link")
            
            # FIXED: Use await for the network call
            shortened_url = await shorten_url(original_link)
            if shortened_url:
                download_links.append({"quality": quality.strip(), "url": shortened_url})
            else:
                await update.message.reply_text(f"⚠️ Failed to shorten link for `{pair}`. Skipping.", parse_mode='Markdown')
                
        except ValueError:
            await msg.edit_text(f"⚠️ **Skipping invalid pair:** `{pair}`. Use `quality:link` format.", parse_mode='Markdown')
            continue

    if not download_links:
        await msg.edit_text("❌ **No valid links provided.** Movie was not added.", parse_mode='Markdown')
        return

    movie_document = {**tmdb_data, "download_links": download_links}

    # FIXED: Use await for the database call
    success, message = await add_movie(movie_document)
    await msg.edit_text(message, parse_mode='Markdown')

async def delete_movie_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /delete command."""
    if not is_admin(update.effective_user.id): return
    if not context.args:
        await update.message.reply_text("⚠️ **Invalid format.**\nUsage: `/delete <TMDb ID>`", parse_mode='Markdown')
        return
    
    try:
        tmdb_id = int(" ".join(context.args))
        # FIXED: Use await for the database call
        success, message = await delete_movie(tmdb_id)
        await update.message.reply_text(message, parse_mode='Markdown')
    except ValueError:
        await update.message.reply_text("⚠️ Please provide a valid numeric TMDb ID.", parse_mode='Markdown')

async def list_movies_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /list command."""
    if not is_admin(update.effective_user.id): return
    # FIXED: Use await for the database call
    all_titles = await list_all_movies()
    if not all_titles:
        await update.message.reply_text("🗂 The database is currently empty.")
        return
    message = "🎬 **All Movies in Database**\n\n" + "\n".join(f"• `{title}`" for title in all_titles)
    # Telegram has a message length limit of 4096 characters
    await update.message.reply_text(message[:4096], parse_mode='Markdown')