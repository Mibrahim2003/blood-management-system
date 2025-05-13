import sys
import os

# Add parent directory to sys.path if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.dirname(parent_dir))

try:
    from database.connection import get_connection
except ImportError:
    try:
        from src.database.connection import get_connection
    except ImportError:
        # If running from the src directory
        try:
            from database.connection import get_connection
        except ImportError:
            raise ImportError("Could not import get_connection, check your Python path")

def fix_blood_requests_table():
    """
    Fix the blood_requests table in case the column name is units_requested instead of units_required
    """
    connection = get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                # Check if units_requested column exists but units_required doesn't
                cursor.execute("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'blood_requests'
                    AND column_name IN ('units_requested', 'units_required')
                """)
                columns = [row[0] for row in cursor.fetchall()]
                
                print(f"Found columns: {columns}")
                
                if 'units_requested' in columns and 'units_required' not in columns:
                    print("Fixing column name: units_requested -> units_required")
                    cursor.execute("""
                        ALTER TABLE blood_requests
                        RENAME COLUMN units_requested TO units_required
                    """)
                    print("Column renamed successfully")
                elif 'units_required' not in columns:
                    print("Creating units_required column")
                    cursor.execute("""
                        ALTER TABLE blood_requests
                        ADD COLUMN units_required INTEGER NOT NULL DEFAULT 1
                    """)
                    print("Column created successfully")
                else:
                    print("No fix needed for blood_requests table")
                  # Make sure units_fulfilled column exists
                cursor.execute("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'blood_requests'
                    AND column_name = 'units_fulfilled'
                """)
                if not cursor.fetchone():
                    print("Adding units_fulfilled column")
                    cursor.execute("""
                        ALTER TABLE blood_requests
                        ADD COLUMN units_fulfilled INTEGER NOT NULL DEFAULT 0
                    """)
                    print("Units fulfilled column added successfully")
                
                # Print the current structure
                cursor.execute("""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = 'blood_requests'
                    ORDER BY ordinal_position
                """)
                print("Current blood_requests table structure:")
                for row in cursor.fetchall():
                    print(f"  {row[0]} ({row[1]})")
    finally:
        connection.close()

def check_blood_units_table():
    """Check and fix common issues in the blood_units table"""
    connection = get_connection()
    try:
        print("Checking blood_units table...")
        with connection:
            with connection.cursor() as cursor:
                # Get the column names of the blood_units table
                cursor.execute("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'blood_units'
                """)
                columns = [row[0] for row in cursor.fetchall()]
                
                if not columns:
                    print("Warning: blood_units table exists but has no columns or doesn't exist")
                    return
                    
                print(f"Found blood_units columns: {columns}")
                
                # Check for common issues with column names
                column_mappings = {
                    "collection_date": "donation_date",
                    "storage_location": "location",
                }
                
                # Fix any mismatched columns
                for expected_col, actual_col in column_mappings.items():
                    if expected_col in columns and actual_col not in columns:
                        print(f"Fixing column name: {expected_col} -> {actual_col}")
                        cursor.execute(f"ALTER TABLE blood_units RENAME COLUMN {expected_col} TO {actual_col}")
                    elif actual_col in columns and expected_col not in columns:
                        # The column already has the correct name
                        print(f"Column {actual_col} already exists, no fix needed")
                
                # Add volume_ml column if it doesn't exist
                if "volume_ml" not in columns:
                    print("Adding missing volume_ml column with default 450ml")
                    cursor.execute("""
                        ALTER TABLE blood_units 
                        ADD COLUMN volume_ml INTEGER NOT NULL DEFAULT 450
                    """)
                
                # Add notes column if it doesn't exist
                if "notes" not in columns:
                    print("Adding missing notes column")
                    cursor.execute("""
                        ALTER TABLE blood_units 
                        ADD COLUMN notes TEXT
                    """)
                    
                # Show the final table structure
                cursor.execute("""
                    SELECT column_name, data_type FROM information_schema.columns
                    WHERE table_name = 'blood_units'
                    ORDER BY ordinal_position
                """)
                print("Final blood_units table structure:")
                for row in cursor.fetchall():
                    print(f"  {row[0]} ({row[1]})")
                    
    except Exception as e:
        print(f"Error checking blood_units table: {str(e)}")
    finally:
        connection.close()

def fix_blood_unit_status_enum():
    """
    Fix the status column in the blood_units table to ensure compatibility with all required status values.
    This will migrate from enum to varchar if needed and ensure all VALID_STATUSES are correctly defined.
    """
    connection = get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                # First check if there's an enum issue
                cursor.execute("""
                    SELECT
                        pg_enum.enumlabel
                    FROM pg_type 
                    JOIN pg_enum ON pg_enum.enumtypid = pg_type.oid 
                    WHERE pg_type.typname = 'blood_unit_status'
                """)
                
                enum_values = [row[0] for row in cursor.fetchall()]
                
                if enum_values:
                    print(f"Found blood_unit_status enum with values: {enum_values}")
                    
                    # Valid statuses that need to be supported
                    valid_statuses = ["Available", "Allocated", "Expired", "Quarantined", "Discarded"]
                    missing_statuses = [status for status in valid_statuses if status not in enum_values]
                    
                    if missing_statuses:
                        print(f"Missing statuses in enum: {missing_statuses}")
                        
                        # The safest approach is to change the column type to varchar
                        print("Changing status column from enum to varchar...")
                        
                        # Create a temporary column, copy data, drop old column, and rename
                        cursor.execute("""
                            ALTER TABLE blood_units ADD COLUMN status_new VARCHAR(20);
                            UPDATE blood_units SET status_new = status::text;
                            ALTER TABLE blood_units DROP COLUMN status;
                            ALTER TABLE blood_units RENAME COLUMN status_new TO status;
                            ALTER TABLE blood_units ALTER COLUMN status SET NOT NULL;
                            ALTER TABLE blood_units ALTER COLUMN status SET DEFAULT 'Available';
                        """)
                        
                        print("Column type changed to VARCHAR(20)")
                else:
                    # Check if the column exists and its type
                    cursor.execute("""
                        SELECT data_type, character_maximum_length, column_default
                        FROM information_schema.columns
                        WHERE table_name = 'blood_units' AND column_name = 'status'
                    """)
                    column_info = cursor.fetchone()
                    
                    if column_info:
                        data_type, max_length, default_value = column_info
                        print(f"Blood unit status column is type: {data_type}, length: {max_length}, default: {default_value}")
                        
                        # If it's already a varchar but too short
                        if data_type == 'character varying' and max_length < 20:
                            print("Increasing varchar length to 20...")
                            cursor.execute("""
                                ALTER TABLE blood_units ALTER COLUMN status TYPE VARCHAR(20);
                            """)
                    else:
                        print("Status column not found in blood_units table")
                
    except Exception as e:
        print(f"Error fixing blood unit status: {str(e)}")
    finally:
        connection.close()

def fix_all_database_tables():
    """Run all database fixing functions"""
    print("Running comprehensive database fixes...")
    fix_blood_requests_table()
    # Blood units functionality has been removed
    print("Database fixes completed")

# Run fixes if this script is run directly
if __name__ == "__main__":
    fix_all_database_tables()
