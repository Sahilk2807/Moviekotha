# tmdb.py
import requests
import logging

TMDB_API_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

def get_movie_details(api_key: str, tmdb_id: int) -> dict | None:
    """
    Fetches movie details from TMDB.

    Args:
        api_key: Your TMDB v3 API key.
        tmdb_id: The movie's TMDB ID.

    Returns:
        A dictionary with movie details or None if not found.
    """
    if not tmdb_id:
        return None
        
    search_url = f"{TMDB_API_URL}/movie/{tmdb_id}"
    params = {'api_key': api_key}

    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        data = response.json()

        return {
            "title": data.get("title", "N/A"),
            "overview": data.get("overview", "No overview available."),
            "release_date": data.get("release_date", "N/A"),
            "poster_url": f"{TMDB_IMAGE_URL}{data.get('poster_path')}" if data.get('poster_path') else None
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"TMDB API request failed for ID {tmdb_id}: {e}")
        return None
    except ValueError:
        logging.error(f"Failed to parse TMDB JSON response for ID {tmdb_id}")
        return None