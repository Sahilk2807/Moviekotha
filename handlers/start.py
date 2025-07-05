# /moviekotha/handlers/start.py

from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a friendly welcome message when the /start command is issued."""
    user = update.effective_user
    welcome_message = (
        f"👋 **Welcome to MovieKotha, {user.first_name}!**\n\n"
        "I'm your personal movie finder bot. I can help you discover movies and get their download links instantly.\n\n"
        "**How to use me:**\n"
        "Simply type the name of the movie you're looking for (at least 3 characters).\n\n"
        "For example: `Inception`\n\n"
        "Let the movie hunt begin! 🎬"
    )
    await update.message.reply_text(welcome_message, parse_mode='Markdown')