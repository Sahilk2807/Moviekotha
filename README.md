# 🎬 MovieKotha - Telegram Movie Download Bot

MovieKotha is a full-featured Telegram bot that allows users to search for movies and get download links for various qualities (4K, 1080p, etc.). It features a powerful admin panel, TMDb integration, and GPLinks URL shortening.

## ✨ Features

- **Multi-Quality Links**: Admins can add multiple download links for different video qualities (e.g., 480p, 720p, 1080p, 4K).
- **Dynamic Buttons**: Users are presented with a separate download button for each available quality.
- **TMDb Integration**: Automatically fetches movie posters, descriptions, and release dates.
- **GPLinks Shortener**: Converts all download links to GPLinks for monetization.
- **MongoDB Atlas Backend**: Uses a powerful and scalable NoSQL database.
- **Admin Panel**: Secure commands for admins to add, delete, and list movies.
- **Smart Search**: Users can find movies by typing at least 3 letters of the title.
- **Deployment Ready**: Configured for easy deployment on platforms like Render or Railway.

## 🚀 Deployment

(Deployment instructions remain the same as previous versions)

## 🤖 Bot Commands

### User Commands
- `/start`: Shows a welcome message.
- `(any text > 3 letters)`: Searches for movies matching the text.

### Admin Commands
- **/add <movie name> <quality1>:<link1> [quality2:link2]...**
  Adds a new movie with one or more download links.
  - **Example (Single Link):**
    `/add Inception 1080p:https://example.com/inception.mkv`
  - **Example (Multiple Links):**
    `/add Oppenheimer 720p:https://.../opp720 1080p:https://.../opp1080 4K:https://.../opp4k`

- `/delete <movie name>`: Removes a movie from the database.
- `/list`: Shows all movies currently in the database.