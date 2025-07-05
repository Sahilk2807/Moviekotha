# /moviekotha/handlers/search.py

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction, ParseMode
from telegram.error import TelegramError
from database import search_movies

LOGGER = logging.getLogger(__name__)

async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles text messages to search for movies."""
    query = update.message.text.strip()

    if len(query) < 3:
        await update.message.reply_text("🤔 Please type at least 3 letters to start a search.")
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    
    results = search_movies(query)
    
    if not results:
        await update.message.reply_text(f"😕 No movies found matching '*{query}*'. Please try a different name.", parse_mode=ParseMode.MARKDOWN)
        return

    for movie in results:
        caption = (
            f"🎬 **{movie.get('title', 'N/A')}**\n\n"
            f"🗓️ **Released:** {movie.get('release_date', 'N/A')}\n\n"
            f"📝 **Plot:**\n{movie.get('description', 'No description available.')}"
        )
        
        keyboard = [[
            InlineKeyboardButton(
                "📥 Get Download Link",
                url=movie.get('shortened_link', 'https://t.me/BotFather')
            )
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        poster_url = movie.get('poster_url')
        try:
            if poster_url:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=poster_url,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            else: # Fallback to text if no poster
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=caption,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup,
                    disable_web_page_preview=True
                )
        except TelegramError as e:
            LOGGER.error(f"Error sending movie '{movie.get('title')}': {e}")
            # Fallback to sending a text message if photo fails for any reason
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=caption,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )