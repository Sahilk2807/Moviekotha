# /moviekotha/config.py

import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
LOGGER = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("🚨 No BOT_TOKEN found in environment variables")

try:
    ADMIN_ID = int(os.getenv("ADMIN_ID"))
    LOGGER.info(f"Admin ID loaded: {ADMIN_ID}")
except (ValueError, TypeError):
    raise ValueError("🚨 ADMIN_ID is not set or not a valid integer")

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_ACCESS_TOKEN = os.getenv("TMDB_ACCESS_TOKEN")
GPLINKS_API = os.getenv("GPLINKS_API")
if not all([TMDB_API_KEY, TMDB_ACCESS_TOKEN, GPLINKS_API]):
    raise ValueError("🚨 One or more API keys (TMDb, GPLinks) are missing")

MONGO_DB_URL = os.getenv("MONGO_DB_URL")
if not MONGO_DB_URL:
    raise ValueError("🚨 No MONGO_DB_URL found in environment variables")