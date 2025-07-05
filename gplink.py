# /moviekotha/gplink.py

import httpx
from config import GPLINKS_API, LOGGER

# --- FIXED: Updated the API URL from .in to .io ---
# The old URL was causing a "301 Moved Permanently" error.
API_URL = "https://gplinks.io/api"

async def shorten_url(original_link: str) -> str | None:
    """Shortens a URL using GPLinks API, now with automatic redirect following."""
    if not GPLINKS_API:
        LOGGER.warning("GPLINKS_API key not set. Returning original link as-is.")
        return original_link
        
    params = {"api": GPLINKS_API, "url": original_link}

    try:
        # Use an async client to make the web request
        async with httpx.AsyncClient() as client:
            
            # --- IMPROVED: Added follow_redirects=True ---
            # This makes the code automatically handle if the API address moves again in the future.
            response = await client.get(API_URL, params=params, follow_redirects=True)
            
            # Check if the final request was successful (status code 200)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    shortened_url = data.get("shortenedUrl")
                    LOGGER.info(f"Successfully shortened link: {shortened_url}")
                    return shortened_url
                else:
                    # The API key might be wrong, or another issue occurred.
                    api_error_message = data.get('message', 'No error message provided.')
                    LOGGER.error(f"GPLinks API returned an error: {api_error_message}")
                    return None
            else:
                # Log other HTTP errors (e.g., 404 Not Found, 500 Server Error)
                LOGGER.error(f"Failed to connect to GPLinks API. Final Status: {response.status_code}")
                return None

    except httpx.RequestError as e:
        LOGGER.error(f"A network error occurred while requesting GPLinks API: {e}")
        return None