# 🎬 MOVIEKOTHA - Telegram Movie Download Bot

MOVIEKOTHA is a full-featured Telegram bot that allows users to search for movies and get direct download links for various qualities. It integrates with TMDB for rich movie data, Google Sheets for a real-time link database, and GPLinks to shorten URLs.

## ✨ Features

- **Intuitive Search**: Users can search for movies by sending a name (case-insensitive, partial matches).
- **Rich Movie Info**: Displays movie posters, titles, overviews, and release dates fetched from TMDB.
- **Real-time Link Database**: Fetches download links directly from a Google Sheet, ensuring data is always up-to-date.
- **Auto URL Shortening**: All download links are automatically converted to short links using GPLinks.
- **Formatted Output**: Presents information cleanly with Markdown styling and emojis.
- **Standard Commands**: Includes `/start`, `/help`, and a `/ping` command to check bot status.
- **Deployment Ready**: Configured for easy deployment on platforms like Render using a `Procfile`.

## 🛠️ Setup & Installation

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd MOVIEKOTHA