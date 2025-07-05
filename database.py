# /moviekotha/database.py

import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from config import MONGO_DB_URL

LOGGER = logging.getLogger(__name__)

try:
    client = MongoClient(MONGO_DB_URL)
    # The ismaster command is cheap and does not require auth.
    client.admin.command('ismaster')
    LOGGER.info("✅ MongoDB connection successful.")
except ConnectionFailure as e:
    LOGGER.error(f"❌ MongoDB connection failed: {e}")
    raise

db = client['moviekotha_db']
movies_collection = db['movies']

def setup_database():
    """Ensures that the necessary index for searching exists."""
    try:
        # Create a case-insensitive index on the 'title' field for faster prefix searches
        movies_collection.create_index([("title", "text")], default_language='none')
        LOGGER.info("✅ Database index checked/created successfully.")
    except OperationFailure as e:
        LOGGER.error(f"❌ Failed to create database index: {e}")


def add_movie(movie_data: dict):
    """Adds a movie document to the collection if it doesn't already exist by TMDb ID."""
    if movies_collection.find_one({"tmdb_id": movie_data["tmdb_id"]}):
        LOGGER.warning(f"Movie '{movie_data['title']}' with TMDb ID {movie_data['tmdb_id']} already exists.")
        return False
    movies_collection.insert_one(movie_data)
    LOGGER.info(f"Added movie '{movie_data['title']}' to the database.")
    return True

def delete_movie(movie_title: str):
    """Deletes a movie from the collection by its title (case-insensitive)."""
    result = movies_collection.delete_one({"title": {"$regex": f"^{movie_title}$", "$options": "i"}})
    return result.deleted_count > 0

def search_movies(query: str):
    """Searches for movies using a text index for better performance."""
    # Using $text search which is more efficient with a text index
    results = movies_collection.find({"$text": {"$search": query}})
    return list(results)

def list_all_movies():
    """Returns a list of all movie titles in the database, sorted alphabetically."""
    all_movies = movies_collection.find({}, {"title": 1, "_id": 0}).sort("title", 1)
    return [movie['title'] for movie in all_movies]