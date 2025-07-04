# 🎬 MOVIEKOTHA - Telegram Movie Download Bot (MySQL Edition)

MOVIEKOTHA is a Telegram bot for searching movies and getting download links. This version uses a robust MySQL backend for storing movie data.

## ✨ Features

- **Intuitive Search**: Search for movies by name.
- **Rich Movie Info**: Fetches posters, overviews, and details from TMDB.
- **Robust Database**: Uses MySQL for a stable and scalable movie link database.
- **In-Bot Admin Panel**: Admins can add new movies using a simple `/addmovie` command.
- **Auto URL Shortening**: All links are shortened via GPLinks.

## 🛠️ Setup & Installation

### Step 1: Set up MySQL Database
- Create a MySQL database from a cloud provider like [PlanetScale](https://planetscale.com/), Aiven, AWS, etc.
- Note down your `host`, `database name`, `user`, and `password`.

### Step 2: Clone & Install Dependencies
```bash
git clone <your-repo-url>
cd MOVIEKOTHA
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt