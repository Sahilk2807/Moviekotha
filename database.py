import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        if conn.is_connected():
            return conn
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def search_movies(query: str):
    """
    Searches for movies in the database with a case-insensitive, partial match.
    """
    conn = get_db_connection()
    if not conn:
        return []

    results = []
    try:
        with conn.cursor(dictionary=True) as cursor:
            # Using LIKE for partial matching and LOWER for case-insensitivity
            sql_query = "SELECT * FROM movies WHERE LOWER(title) LIKE LOWER(%s)"
            # Add wildcards for partial matching
            search_term = f"%{query}%"
            cursor.execute(sql_query, (search_term,))
            results = cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Error executing search query: {e}")
    finally:
        if conn.is_connected():
            conn.close()
            
    return results

def check_db_connection():
    """A simple function to check if the database connection is alive."""
    conn = get_db_connection()
    if conn:
        conn.close()
        return True
    return False