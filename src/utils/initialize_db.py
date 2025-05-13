import os
import psycopg2
from database.connection import get_connection
from utils.fix_database import fix_blood_requests_table
from utils.fix_blood_units import create_blood_units_table

def initialize_database():
    """Initialize the database with the required tables and default data."""
    conn = None
    try:
        # Get connection
        conn = get_connection()
        if not conn:
            print("Error: Could not connect to the database.")
            return False
            
        # Read SQL file
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sql_file_path = os.path.join(base_path, 'utils', 'blood_donation.sql')
        
        # Read SQL commands from file
        with open(sql_file_path, 'r') as f:
            sql_script = f.read()
          # Execute SQL commands
        cursor = conn.cursor()
        cursor.execute(sql_script)
        conn.commit()
        cursor.close()
          # Fix any database schema issues
        fix_blood_requests_table()
        
        # Ensure Blood_Units table exists
        create_blood_units_table()
        
        print("Database initialized successfully.")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # When run directly, initialize the database
    initialize_database()
