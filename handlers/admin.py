# /moviekotha/handlers/admin.py

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from config import ADMIN_ID
from database import add_movie, delete_movie, list_all_movies
from tmdb import search_movie_tmdb
from gplink import shorten_url

def is_admin(user_id: int) -> bool:
    """A simple check to see if the user is the admin."""
    return user_id == ADMIN_ID

async def add_movie_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /add command to add a new movie."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔️ Sorry, this command is for admins only.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("⚠️ **Invalid format.**\nUsage: `/add <Movie Name> <Download Link>`")
        return

    download_link = context.args[-1]
    movie_name = " ".join(context.args[:-1])

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    msg = await update.message.reply_text(f"Fetching details for *{movie_name}*...", parse_mode='Markdown')

    tmdb_data = search_movie_tmdb(movie_name)
    if not tmdb_data:
        await msg.edit_text(f"❌ **Movie not found!**\nCould not find '{movie_name}' on TMDb. Please check the spelling.")
        return

    await msg.edit_text("Shortening download link...")
    shortened_link = shorten_url(download_link)

    movie_document = {**tmdb_data, "original_link": download_link, "shortened_link": shortened_link}

    if add_movie(movie_document):
        await msg.edit_text(f"✅ **Success!**\nMovie '{tmdb_data['title']}' has been added to the database.")
    else:
        await msg.edit_text(f"🔵 **Already Exists!**\nMovie '{tmdb_data['title']}' is already in the database.")


async def delete_movie_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /delete command."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔️ Sorry, this command is for admins only.")
        return
        
    if not context.args:
        await update.message.reply_text("⚠️ **Invalid format.**\nUsage: `/delete <Movie Name>`")
        return
        
    movie_name = " ".join(context.args)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    if delete_movie(movie_name):
        await update.message.reply_text(f"✅ **Success!**\n'{movie_name}' has been deleted from the database.")
    else:
        await update.message.reply_text(f"❌ **Not Found!**\nCould not find a movie with the exact name '{movie_name}'.")

async def list_movies_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /list command to show all movies."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔️ Sorry, this command is for admins only.")
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    all_titles = list_all_movies()
    
    if not all_titles:
        await update.message.reply_text("🗂 The database is currently empty.")
        return
        
    message = "🎬 **All Movies in Database**\n\n"
    message += "\n".join(f"• `{title}`" for title in all_titles)
    
    if len(message) > 4096:
        message = message[:4090] + "\n..." # Truncate if too long
        
    await update.message.reply_text(message, parse_mode='Markdown')