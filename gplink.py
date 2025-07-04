# gplink.py
import requests
import logging

def shorten_url(api_key: str, long_url: str) -> str:
    """
    Shortens a URL using the GPLinks API.

    Args:
        api_key: Your GPLinks API key.
        long_url: The URL to shorten.

    Returns:
        The shortened URL, or the original URL if an error occurs.
    """
    if not api_key or not long_url:
        return long_url

    api_url = f"https://gplinks.in/api?api={api_key}&url={long_url}"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()

        if data.get("status") == "success":
            return data.get("shortenedUrl", long_url)
        else:
            logging.error(f"GPLinks API error: {data.get('message', 'Unknown error')}")
            return long_url
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to connect to GPLinks API: {e}")
        return long_url
    except ValueError:
        logging.error(f"Failed to parse GPLinks JSON response: {response.text}")
        return long_url