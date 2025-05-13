from database.connection import get_connection
import psycopg2
import psycopg2.extras

class ReceiverRepository:
    def __init__(self):
        self.connection = None

    def connect(self):
        if self.connection is None:
            self.connection = get_connection()

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def add_receiver(self, first_name, last_name, dob, gender, blood_type_id, reason_for_transfusion, hospital_name, ward_details, contact_person_name, contact_person_phone):
        self.connect()
        print(f"Attempting to add receiver: {first_name} {last_name}")
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Receivers (first_name, last_name, dob, gender, blood_type_id, reason_for_transfusion, hospital_name, ward_details, contact_person_name, contact_person_phone)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING receiver_id
                """, (first_name, last_name, dob, gender, blood_type_id, reason_for_transfusion, hospital_name, ward_details, contact_person_name, contact_person_phone))
                
                receiver_id = cursor.fetchone()[0]
                self.connection.commit()
                print(f"Receiver added successfully with ID: {receiver_id}")
                return True
        except Exception as e:
            print(f"Error adding receiver: {e}")
            import traceback
            traceback.print_exc()
            self.connection.rollback()
            return False

    def get_all_receivers(self):
        self.connect()
        try:
            with self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:                
                # Get all receivers with their blood types
                cursor.execute("""
                    SELECT r.*, bt.type_name as blood_type 
                    FROM Receivers r
                    JOIN Blood_Types bt ON r.blood_type_id = bt.blood_type_id
                    ORDER BY r.first_name, r.last_name
                """)
                receivers = cursor.fetchall()
                print(f"Found {len(receivers)} receivers in the database")
                return receivers
        except Exception as e:
            print(f"Error getting receivers: {e}")
            import traceback
            traceback.print_exc()
            
            try:
                # Fallback: Get receivers without joining to Blood_Types
                with self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM Receivers
                        ORDER BY first_name, last_name
                    """)
                    receivers = cursor.fetchall()
                    print(f"Fallback query found {len(receivers)} receivers")
                    return receivers
            except Exception as e2:
                print(f"Error in fallback query: {e2}")
                return []

    def search_receivers(self, search_term):
        self.connect()
        try:
            with self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("""
                    SELECT r.*, bt.type_name as blood_type
                    FROM Receivers r
                    JOIN Blood_Types bt ON r.blood_type_id = bt.blood_type_id
                    WHERE 
                        LOWER(r.first_name) LIKE %s OR
                        LOWER(r.last_name) LIKE %s OR
                        LOWER(r.hospital_name) LIKE %s OR
                        LOWER(bt.type_name) LIKE %s
                    ORDER BY r.first_name, r.last_name
                """, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
                results = cursor.fetchall()
                print(f"Found {len(results)} receivers matching '{search_term}'")
                return results
        except Exception as e:
            print(f"Error searching receivers: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_receiver_by_id(self, receiver_id):
        self.connect()
        try:
            with self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("""
                    SELECT r.*, bt.type_name as blood_type
                    FROM Receivers r
                    JOIN Blood_Types bt ON r.blood_type_id = bt.blood_type_id
                    WHERE r.receiver_id = %s
                """, (receiver_id,))
                receiver = cursor.fetchone()
                if receiver:
                    print(f"Found receiver with ID {receiver_id}: {receiver['first_name']} {receiver['last_name']}")
                else:
                    print(f"No receiver found with ID {receiver_id}")
                return receiver
        except Exception as e:
            print(f"Error getting receiver by ID: {e}")
            import traceback
            traceback.print_exc()
            return None

    def update_receiver(self, receiver_id, first_name, last_name, dob, gender, blood_type_id, reason_for_transfusion, hospital_name, ward_details, contact_person_name, contact_person_phone):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE Receivers
                    SET first_name = %s, last_name = %s, dob = %s, gender = %s, blood_type_id = %s, 
                        reason_for_transfusion = %s, hospital_name = %s, ward_details = %s, 
                        contact_person_name = %s, contact_person_phone = %s
                    WHERE receiver_id = %s
                """, (first_name, last_name, dob, gender, blood_type_id, reason_for_transfusion, 
                      hospital_name, ward_details, contact_person_name, contact_person_phone, receiver_id))
                self.connection.commit()
                return True
        except Exception as e:
            print(f"Error updating receiver: {e}")
            self.connection.rollback()
            return False

    def delete_receiver(self, receiver_id):
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM Receivers WHERE receiver_id = %s", (receiver_id,))
                self.connection.commit()
                return True
        except Exception as e:
            print(f"Error deleting receiver: {e}")
            self.connection.rollback()
            return False