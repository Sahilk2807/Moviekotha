# /moviekotha/gplink.py

import requests
import logging
from config import GPLINKS_API

LOGGER = logging.getLogger(__name__)

def shorten_url(long_url: str):
    """
    Shortens a given URL using GPLinks API.
    Returns the original URL if shortening fails.
    """
    api_url = "https://gplinks.in/api"
    params = {'api': GPLINKS_API, 'url': long_url}
    
    try:
        response = requests.get(api_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "success":
            LOGGER.info(f"Successfully shortened URL: {long_url}")
            return data.get("shortenedUrl")
        else:
            LOGGER.error(f"GPLinks API Error: {data.get('message', 'Unknown error')}")
            return long_url
    except requests.exceptions.RequestException as e:
        LOGGER.error(f"Error calling GPLinks API: {e}")
        return long_url