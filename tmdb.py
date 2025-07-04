import requests
import os

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

def get_movie_details(tmdb_id: int):
    """Fetches detailed movie information from TMDB using its ID."""
    if not tmdb_id:
        return None
        
    url = f"{TMDB_BASE_URL}/movie/{tmdb_id}?api_key={TMDB_API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        
        poster_path = data.get("poster_path")
        
        return {
            "title": data.get("title", "N/A"),
            "overview": data.get("overview", "No overview available."),
            "release_date": data.get("release_date", "N/A"),
            "poster_url": f"{POSTER_BASE_URL}{poster_path}" if poster_path else "https://via.placeholder.com/500x750.png?text=No+Poster"
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from TMDB: {e}")
        return None