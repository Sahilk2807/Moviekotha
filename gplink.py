# /moviekotha/gplink.py

import httpx
from config import GPLINKS_API, LOGGER

API_URL = "https://gplinks.in/api"

async def shorten_url(original_link: str) -> str | None:
    """Shortens a URL using GPLinks API."""
    if not GPLINKS_API:
        LOGGER.warning("GPLINKS_API key not set. Returning original link.")
        return original_link
        
    params = {"api": GPLINKS_API, "url": original_link}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(API_URL, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    LOGGER.info(f"Successfully shortened link: {data['shortenedUrl']}")
                    return data["shortenedUrl"]
                else:
                    LOGGER.error(f"GPLinks API error: {data.get('message')}")
                    return None
            else:
                LOGGER.error(f"Failed to connect to GPLinks API. Status: {response.status_code}")
                return None
    except httpx.RequestError as e:
        LOGGER.error(f"An error occurred while requesting GPLinks API: {e}")
        return None