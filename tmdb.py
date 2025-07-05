# /moviekotha/tmdb.py

import httpx
from config import TMDB_API_KEY, LOGGER

SEARCH_API_URL = "https://api.themoviedb.org/3/search/movie"
DETAILS_API_URL = "https://api.themoviedb.org/3/movie/{}"

async def search_movie_by_name(query: str) -> dict | None:
    """Searches for a movie by name and returns a structured dict of the best match."""
    params = {"api_key": TMDB_API_KEY, "query": query}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(SEARCH_API_URL, params=params)
            if response.status_code != 200:
                LOGGER.error(f"TMDb search failed with status {response.status_code}")
                return None
            
            results = response.json().get("results")
            if not results:
                return None

            # Get the first and most relevant result
            best_match = results[0]
            movie_id = best_match.get("id")

            # Now fetch full details to get genres, etc.
            details_response = await client.get(DETAILS_API_URL.format(movie_id), params={"api_key": TMDB_API_KEY})
            if details_response.status_code != 200:
                return None # Failed to get details, so we can't proceed
            
            details = details_response.json()
            
            # Create a clean, structured document
            return {
                "_id": details.get("id"),
                "title": details.get("title"),
                "original_title": details.get("original_title"),
                "year": details.get("release_date", "----").split("-")[0],
                "overview": details.get("overview"),
                "poster_path": details.get("poster_path"),
                "genres": [genre["name"] for genre in details.get("genres", [])],
                "rating": details.get("vote_average")
            }
    except httpx.RequestError as e:
        LOGGER.error(f"An error occurred while requesting TMDb: {e}")
        return None