# database.py
import mysql.connector
import os
import logging

def create_connection():
    """Create a database connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE")
        )
        if connection.is_connected():
            logging.info("Successfully connected to the database.")
            return connection
    except mysql.connector.Error as e:
        logging.error(f"Error connecting to MySQL Database: {e}")
        return None

def initialize_database():
    """Create the movies table if it doesn't exist."""
    conn = create_connection()
    if conn is None:
        logging.critical("Could not create database connection. Aborting table initialization.")
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tmdb_id INT UNIQUE NOT NULL,
                title VARCHAR(255) NOT NULL,
                short_description TEXT,
                link_480p TEXT,
                link_720p TEXT,
                link_1080p TEXT,
                link_x265 TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logging.info("Database initialized. 'movies' table is ready.")
    except mysql.connector.Error as e:
        logging.error(f"Error creating table: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def search_movies(query: str) -> list:
    """Search for movies in the database."""
    conn = create_connection()
    if conn is None: return []

    results = []
    try:
        cursor = conn.cursor(dictionary=True) # Fetch as dictionaries
        # Use LIKE for partial, case-insensitive search
        sql_query = "SELECT * FROM movies WHERE title LIKE %s"
        search_term = f"%{query}%"
        cursor.execute(sql_query, (search_term,))
        results = cursor.fetchall()
        return results
    except mysql.connector.Error as e:
        logging.error(f"Error searching for movies: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def check_movie_exists(tmdb_id: int) -> bool:
    """Check if a movie already exists by its TMDB ID."""
    conn = create_connection()
    if conn is None: return True # Fail-safe to prevent duplicates
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM movies WHERE tmdb_id = %s", (tmdb_id,))
        exists = cursor.fetchone() is not None
        return exists
    except mysql.connector.Error as e:
        logging.error(f"Error checking movie existence: {e}")
        return True
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def add_movie(movie_data: dict) -> bool:
    """Add a new movie to the database."""
    conn = create_connection()
    if conn is None: return False

    sql = """
        INSERT INTO movies 
        (tmdb_id, title, short_description, link_480p, link_720p, link_1080p, link_x265) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (
            movie_data.get('tmdb_id'),
            movie_data.get('title'),
            movie_data.get('short_description'),
            movie_data.get('link_480p'),
            movie_data.get('link_720p'),
            movie_data.get('link_1080p'),
            movie_data.get('link_x265')
        ))
        conn.commit()
        logging.info(f"Successfully added movie: {movie_data.get('title')}")
        return True
    except mysql.connector.Error as e:
        logging.error(f"Error adding movie: {e}")
        conn.rollback()
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()