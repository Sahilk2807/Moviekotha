# /moviekotha/tmdb.py

import requests
import logging
from urllib.parse import quote
from config import TMDB_API_KEY, TMDB_ACCESS_TOKEN

LOGGER = logging.getLogger(__name__)

def search_movie_tmdb(movie_name: str):
    """Searches TMDb and returns metadata for the first result."""
    encoded_movie_name = quote(movie_name)
    url = f"https://api.themoviedb.org/3/search/movie?query={encoded_movie_name}&include_adult=false&language=en-US&page=1"
    headers = {"accept": "application/json", "Authorization": f"Bearer {TMDB_ACCESS_TOKEN}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data.get("results"):
            movie = data["results"][0]
            poster_path = movie.get("poster_path")
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

            return {
                "tmdb_id": movie.get("id"),
                "title": movie.get("title"),
                "description": movie.get("overview", "No description available."),
                "release_date": movie.get("release_date"),
                "poster_url": poster_url
            }
    except requests.exceptions.RequestException as e:
        LOGGER.error(f"Error fetching data from TMDb: {e}")
    return None