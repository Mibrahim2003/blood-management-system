import psycopg2
# Use relative import instead of absolute import
from .db_config import config

def get_connection():
    """Establish and return a new database connection."""
    try:
        params = config()  # reads 'postgresql' section from database.ini
        conn = psycopg2.connect(**params)
        return conn
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

def test_connection():
    """Quick test to verify everything's working."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT current_database(), current_user;")
        db, user = cur.fetchone()
        print(f"Connected to database '{db}' as user '{user}'")
        cur.close()
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False
    finally:
        if conn is not None:
            conn.close()