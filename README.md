# 🎬 MovieKotha - Telegram Movie Download Bot

MovieKotha is a full-featured Telegram bot built with Python that allows users to search for movies and get download links. It features an admin panel for managing the movie database, integrates with TMDb for metadata and GPLinks for URL shortening.

## ✨ Features

- **TMDb Integration**: Automatically fetches movie posters, descriptions, and release dates.
- **GPLinks Shortener**: Converts all download links to GPLinks for monetization.
- **MongoDB Atlas Backend**: Uses a powerful and scalable NoSQL database for storing movie data.
- **Admin Panel**: Secure commands for admins to add, delete, and list movies.
- **Smart Search**: Users can find movies by typing at least 3 letters of the title.
- **User-Friendly Interface**: Uses emojis, animations, and interactive buttons.
- **Deployment Ready**: Configured for easy deployment on platforms like Render or Railway.

## 🚀 Deployment

### 1. Prerequisites

- A Telegram Bot Token from [@BotFather](https://t.me/BotFather).
- A TMDb API Key and Access Token (Bearer Token).
- A GPLinks API Token.
- A MongoDB Atlas account and a Connection URL.
- Your numeric Telegram User ID for admin access.

### 2. Setup on Render / Railway

1.  **Fork this repository** on GitHub.
2.  Go to your Render (or Railway) dashboard and create a **New Web Service** or **Background Worker**.
3.  Connect the forked GitHub repository.
4.  Set the **Start Command** to `python main.py`.
5.  Go to the **Environment** tab and add the following environment variables:

| Variable            | Description                               | Example Value                         |
| ------------------- | ----------------------------------------- | ------------------------------------- |
| `BOT_TOKEN`         | Your Telegram bot token.                  | `123456:ABC-DEF1234ghIkl-zyx57W2v1u123`|
| `ADMIN_ID`          | Your numeric Telegram User ID.            | `123456789`                           |
| `TMDB_API_KEY`      | The Movie Database (TMDb) v3 API Key.     | `your_tmdb_api_key`                   |
| `TMDB_ACCESS_TOKEN` | TMDb API Read Access Token (v4 Bearer).   | `your_tmdb_access_token`              |
| `GPLINKS_API`       | Your GPLinks API token.                   | `your_gplinks_api_token`              |
| `MONGO_DB_URL`      | Your MongoDB Atlas connection string.     | `mongodb+srv://user:pass@cluster...`  |

6.  Deploy the service. The bot will start automatically.

## 🤖 Bot Commands

### User Commands
- `/start`: Shows a welcome message.
- `(any text > 3 letters)`: Searches for movies matching the text.

### Admin Commands
- `/add <movie name> <download link>`: Adds a new movie to the database.
- `/delete <movie name>`: Removes a movie from the database.
- `/list`: Shows all movies currently in the database.