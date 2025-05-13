from typing import List, Dict, Any, Optional
import psycopg2
from database.db_config import config
from database.connection import get_connection

class BloodRequestRepo:
    @staticmethod
    def create_request(receiver_id: int, blood_type_id: int, units_required: int, 
                     priority: str = 'Medium', notes: str = None) -> int:
        """Create a new blood request and return the request_id"""
        connection = get_connection()
        try:
            # Map common priority names to valid enum values
            priority_map = {
                'Normal': 'Medium',  # Map Normal to Medium
                'Critical': 'Urgent',  # Map Critical to Urgent
                # Other values (Urgent, High, Medium, Low) will be used as-is
            }
            # Use the mapped value if it exists, otherwise use the original
            actual_priority = priority_map.get(priority, priority)
            
            # Ensure priority is one of the valid values
            valid_priorities = ['Urgent', 'High', 'Medium', 'Low']
            if actual_priority not in valid_priorities:
                actual_priority = 'Medium'  # Default to Medium if invalid
                
            with connection:
                with connection.cursor() as cursor:
                    # First check if the 'notes' column exists
                    cursor.execute("""
                        SELECT column_name FROM information_schema.columns
                        WHERE table_name = 'blood_requests' AND column_name = 'notes'
                    """)
                    notes_column_exists = cursor.fetchone() is not None
                    
                    # Create the SQL statement based on whether notes column exists
                    if notes_column_exists:
                        cursor.execute("""
                            INSERT INTO Blood_Requests 
                            (receiver_id, blood_type_id, units_required, priority, status, notes)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            RETURNING request_id
                        """, (receiver_id, blood_type_id, units_required, actual_priority, 'Pending', notes))
                    else:
                        # Insert without notes column
                        cursor.execute("""
                            INSERT INTO Blood_Requests 
                            (receiver_id, blood_type_id, units_required, priority, status)
                            VALUES (%s, %s, %s, %s, %s)
                            RETURNING request_id
                        """, (receiver_id, blood_type_id, units_required, actual_priority, 'Pending'))
                        
                    request_id = cursor.fetchone()[0]
                    return request_id
        finally:
            connection.close()

    @staticmethod
    def update_request_status(request_id: int, status: str) -> None:
        """Update the status of a blood request"""
        connection = get_connection()
        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE Blood_Requests
                        SET status = %s
                        WHERE request_id = %s
                    """, (status, request_id))
        finally:
            connection.close()
            
    @staticmethod
    def update_units_fulfilled(request_id: int, units_fulfilled: int) -> None:
        """Update the number of units fulfilled for a blood request"""
        connection = get_connection()
        try:
            # Check if units_fulfilled column exists
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT column_name FROM information_schema.columns
                        WHERE table_name = 'blood_requests' AND column_name = 'units_fulfilled'
                    """)
                    has_units_fulfilled = cursor.fetchone() is not None
                    
                    if not has_units_fulfilled:
                        # Add the units_fulfilled column if it doesn't exist
                        cursor.execute("""
                            ALTER TABLE Blood_Requests
                            ADD COLUMN units_fulfilled INTEGER DEFAULT 0
                        """)
                    
                    # Update the units_fulfilled value
                    cursor.execute("""
                        UPDATE Blood_Requests
                        SET units_fulfilled = %s
                        WHERE request_id = %s
                    """, (units_fulfilled, request_id))
                    
                    # Get units required to check if we're done
                    cursor.execute("""
                        SELECT units_required 
                        FROM Blood_Requests 
                        WHERE request_id = %s
                    """, (request_id,))
                    
                    units_required = cursor.fetchone()[0]
                    
                    print(f"Checking if request {request_id} is fulfilled: {units_fulfilled} >= {units_required}")
                    
                    # If all units are fulfilled, update status to "Fulfilled"
                    if units_fulfilled >= units_required:
                        print(f"Setting request {request_id} status to Fulfilled")
                        cursor.execute("""
                            UPDATE Blood_Requests
                            SET status = 'Fulfilled'
                            WHERE request_id = %s 
                            AND status != 'Cancelled'
                        """, (request_id,))
        finally:
            connection.close()

    # Blood unit assignment functionality

    @staticmethod
    def get_all_requests(status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all blood requests with receiver and blood type information"""
        connection = get_connection()
        try:
            with connection:
                with connection.cursor() as cursor:
                    # First check if notes column exists
                    cursor.execute("""
                        SELECT column_name FROM information_schema.columns
                        WHERE table_name = 'blood_requests' AND column_name = 'notes'
                    """)
                    notes_column_exists = cursor.fetchone() is not None
                    
                    # Check if units_fulfilled column exists
                    cursor.execute("""
                        SELECT column_name FROM information_schema.columns
                        WHERE table_name = 'blood_requests' AND column_name = 'units_fulfilled'
                    """)
                    has_units_fulfilled = cursor.fetchone() is not None
                    
                    query = """
                        SELECT br.request_id, br.receiver_id, 
                               r.first_name || ' ' || r.last_name as receiver_name,
                               br.blood_type_id, bt.type_name as blood_type,
                               br.units_required, br.request_date, br.priority, br.status,
                    """
                    
                    # Add units_fulfilled column if it exists
                    if has_units_fulfilled:
                        query += " COALESCE(br.units_fulfilled, 0) as units_fulfilled,"
                    else:
                        query += " 0 as units_fulfilled,"
                    
                    # Add notes column to query if it exists
                    if notes_column_exists:
                        query += " br.notes,"
                    
                    query += """
                               COALESCE(br.units_fulfilled, 0) as units_assigned
                        FROM Blood_Requests br
                        JOIN Receivers r ON br.receiver_id = r.receiver_id
                        JOIN Blood_Types bt ON br.blood_type_id = bt.blood_type_id
                    """
                    
                    if status:
                        query += " WHERE br.status = %s"
                        query += " GROUP BY br.request_id, r.first_name, r.last_name, bt.type_name"
                        query += " ORDER BY br.request_date DESC"
                        cursor.execute(query, (status,))
                    else:
                        query += " GROUP BY br.request_id, r.first_name, r.last_name, bt.type_name"
                        query += " ORDER BY br.request_date DESC"
                        cursor.execute(query)
                    
                    columns = [desc[0] for desc in cursor.description]
                    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    
                    # Add empty notes if the column doesn't exist
                    if not notes_column_exists:
                        for result in results:
                            result['notes'] = ''
                    
                    return results
        finally:
            connection.close()
    
    @staticmethod
    def get_request_by_id(request_id: int) -> Dict[str, Any]:
        """Get a specific blood request by ID with receiver and blood type information"""
        connection = get_connection()
        try:
            with connection:
                with connection.cursor() as cursor:
                    # First check if notes column exists
                    cursor.execute("""
                        SELECT column_name FROM information_schema.columns
                        WHERE table_name = 'blood_requests' AND column_name = 'notes'
                    """)
                    notes_column_exists = cursor.fetchone() is not None
                    
                    # Check if units_fulfilled column exists
                    cursor.execute("""
                        SELECT column_name FROM information_schema.columns
                        WHERE table_name = 'blood_requests' AND column_name = 'units_fulfilled'
                    """)
                    has_units_fulfilled = cursor.fetchone() is not None
                    
                    query = """
                        SELECT br.request_id, br.receiver_id, 
                               r.first_name || ' ' || r.last_name as receiver_name,
                               br.blood_type_id, bt.type_name as blood_type,
                               br.units_required, br.request_date, br.priority, br.status,
                    """
                    
                    # Add units_fulfilled column if it exists
                    if has_units_fulfilled:
                        query += " COALESCE(br.units_fulfilled, 0) as units_fulfilled,"
                    else:
                        query += " 0 as units_fulfilled,"
                    
                    # Add notes column to query if it exists
                    if notes_column_exists:
                        query += " br.notes,"
                    
                    query += """
                               COALESCE(br.units_fulfilled, 0) as units_assigned
                        FROM Blood_Requests br
                        JOIN Receivers r ON br.receiver_id = r.receiver_id
                        JOIN Blood_Types bt ON br.blood_type_id = bt.blood_type_id
                        WHERE br.request_id = %s
                    """
                    
                    cursor.execute(query, (request_id,))
                    
                    columns = [desc[0] for desc in cursor.description]
                    result = cursor.fetchone()
                    data = dict(zip(columns, result)) if result else None
                    
                    # Add empty notes if the column doesn't exist
                    if data and not notes_column_exists:
                        data['notes'] = ''
                        
                    return data
        finally:
            connection.close()
    
    @staticmethod
    def search_requests(search_term: str) -> List[Dict[str, Any]]:
        """Search for blood requests by receiver name, blood type, status, or priority"""
        connection = get_connection()
        search_pattern = f"%{search_term}%"
        try:
            with connection:
                with connection.cursor() as cursor:
                    # First check if notes column exists
                    cursor.execute("""
                        SELECT column_name FROM information_schema.columns
                        WHERE table_name = 'blood_requests' AND column_name = 'notes'
                    """)
                    notes_column_exists = cursor.fetchone() is not None
                    
                    query = """
                        SELECT br.request_id, br.receiver_id, 
                               r.first_name || ' ' || r.last_name as receiver_name,
                               br.blood_type_id, bt.type_name as blood_type,
                               br.units_required, br.request_date, br.priority, br.status,
                    """
                    
                    # Add notes column to query if it exists
                    if notes_column_exists:
                        query += " br.notes,"
                    
                    query += """
                               0 as units_assigned
                        FROM Blood_Requests br
                        JOIN Receivers r ON br.receiver_id = r.receiver_id
                        JOIN Blood_Types bt ON br.blood_type_id = bt.blood_type_id
                        WHERE r.first_name ILIKE %s 
                           OR r.last_name ILIKE %s
                           OR bt.type_name ILIKE %s
                           OR br.status::text ILIKE %s
                           OR br.priority::text ILIKE %s
                        GROUP BY br.request_id, r.first_name, r.last_name, bt.type_name
                        ORDER BY br.request_date DESC
                    """
                    
                    cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
                    
                    columns = [desc[0] for desc in cursor.description]
                    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    
                    # Add empty notes if the column doesn't exist
                    if not notes_column_exists:
                        for result in results:
                            result['notes'] = ''
                    
                    return results
        finally:
            connection.close()
            
        # Blood unit compatibility functionality has been removed
        
        connection = get_connection()
        try:
            with connection:
                with connection.cursor() as cursor:
                    # First check the actual schema of blood_units table
                    cursor.execute("""
                        SELECT column_name FROM information_schema.columns
                        WHERE table_name = 'blood_units'
                    """)
                    available_columns = [row[0] for row in cursor.fetchall()]
                    
                    # Determine the correct column names based on what's in the database
                    date_column = "donation_date" if "donation_date" in available_columns else "collection_date"
                    location_column = "location" if "location" in available_columns else "storage_location"
                    
                    compatible_types = compatibility.get(blood_type_id, [])
                    if not compatible_types:
                        return []
                    
                    placeholders = ", ".join(["%s"] * len(compatible_types))
                    
                    # Build the query with the correct column names and include donor information
                    query = f"""
                        SELECT bu.unit_id, bu.blood_type_id, bt.type_name, 
                               bu.{date_column}, bu.expiry_date, 
                               d.donor_id, d.first_name || ' ' || d.last_name as donor_name,
                    """
                    
                    # Add volume_ml if it exists, otherwise use a constant
                    if "volume_ml" in available_columns:
                        query += "bu.volume_ml, "
                    else:
                        query += "'450' as volume_ml, "  # Standard volume for a blood bag
                    
                    query += f"""
                               bu.{location_column}
                        FROM Blood_Units bu
                        JOIN Blood_Types bt ON bu.blood_type_id = bt.blood_type_id
                        JOIN Donors d ON bu.donor_id = d.donor_id
                        WHERE bu.status = 'Available' 
                        AND bu.blood_type_id IN ({placeholders})
                        ORDER BY bu.expiry_date ASC
                    """
                    
                    cursor.execute(query, compatible_types)
                    
                    columns = [desc[0] for desc in cursor.description]
                    return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            connection.close()
    
        # Blood unit assignment functionality has been removed

