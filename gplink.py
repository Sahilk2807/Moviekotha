import requests
import os

GP_API_KEY = os.getenv("GP_API_KEY")
GP_API_URL = "https://gplinks.in/api"

def shorten_url(long_url: str):
    """Shortens a URL using GPLinks API."""
    if not long_url or not long_url.strip():
        return None

    params = {
        'api': GP_API_KEY,
        'url': long_url
    }
    
    try:
        response = requests.get(GP_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "success":
            return data.get("shortenedUrl")
        else:
            print(f"GPLink API Error: {data.get('message', 'Unknown error')}")
            return long_url # Return original URL on failure
    except requests.exceptions.RequestException as e:
        print(f"Error calling GPLinks API: {e}")
        return long_url # Return original URL on failure