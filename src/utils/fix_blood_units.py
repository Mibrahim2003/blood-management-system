from database.connection import get_connection

def create_blood_units_table():
    """
    Create the Blood_Units table if it doesn't exist.
    This fixes the issue where the table was dropped but not recreated.
    """
    conn = None
    try:
        conn = get_connection()
        if not conn:
            print("Error: Could not connect to the database.")
            return False
            
        cursor = conn.cursor()
        
        # Check if the table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'blood_units'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("Creating Blood_Units table...")
            # Create the blood_units table
            cursor.execute("""
                CREATE TABLE Blood_Units (
                    unit_id SERIAL PRIMARY KEY,
                    donor_id INTEGER REFERENCES Donors(donor_id),
                    blood_type_id INTEGER NOT NULL REFERENCES Blood_Types(blood_type_id),
                    collection_date DATE NOT NULL,
                    expiration_date DATE NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'Available',
                    storage_location VARCHAR(100),
                    volume_ml INTEGER DEFAULT 450
                );
            """)
            conn.commit()
            print("Blood_Units table created successfully.")
        else:
            print("Blood_Units table already exists.")
            
        cursor.close()
        return True
    except Exception as e:
        print(f"Error creating Blood_Units table: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # When run directly, create the Blood_Units table
    create_blood_units_table()