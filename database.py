import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to database: {e}")
        return None

def search_movies(query: str):
    """Searches for movies in the database (case-insensitive)."""
    conn = get_db_connection()
    if not conn:
        return []
    
    results = []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # ILIKE is the case-insensitive version of LIKE in PostgreSQL
            sql_query = "SELECT * FROM movies WHERE title ILIKE %s"
            search_term = f"%{query}%"
            cur.execute(sql_query, (search_term,))
            results = cur.fetchall()
    except psycopg2.Error as e:
        print(f"Database search error: {e}")
    finally:
        if conn:
            conn.close()
    return results

def add_movie(title: str, tmdb_id: int, links: dict):
    """Adds a new movie to the database."""
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed."

    try:
        with conn.cursor() as cur:
            sql_query = """
            INSERT INTO movies (title, tmdb_id, link_480p, link_720p, link_1080p, link_x265)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (
                title,
                tmdb_id,
                links.get('480p'),
                links.get('720p'),
                links.get('1080p'),
                links.get('x265')
            )
            cur.execute(sql_query, params)
            conn.commit()
            return True, f"Successfully added '{title}'."
    except psycopg2.Error as e:
        conn.rollback() # Roll back the transaction on error
        if e.pgcode == '23505':  # Unique violation error code for PostgreSQL
            return False, f"Error: Movie '{title}' already exists in the database."
        return False, f"Database error: {e}"
    finally:
        if conn:
            conn.close()