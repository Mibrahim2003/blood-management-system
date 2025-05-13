from database.connection import get_connection
import datetime

class DonorRepository:
    def get_all_donors(self):
        """Get all donors from the database."""
        conn = None
        donors = []
        
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            query = """
            SELECT d.donor_id, d.first_name, d.last_name, d.dob, d.gender,
                   bt.type_name, d.phone_number, d.email, d.address,
                   d.registration_date, d.last_donation_date
            FROM Donors d
            JOIN Blood_Types bt ON d.blood_type_id = bt.blood_type_id
            ORDER BY d.last_name, d.first_name;
            """
            
            cur.execute(query)
            rows = cur.fetchall()
            
            for row in rows:
                donors.append({
                    "donor_id": row[0],
                    "first_name": row[1],
                    "last_name": row[2],
                    "dob": row[3],
                    "gender": row[4],
                    "blood_type": row[5],
                    "phone_number": row[6],
                    "email": row[7],
                    "address": row[8],
                    "registration_date": row[9],
                    "last_donation_date": row[10]
                })
            
            cur.close()
        except Exception as e:
            print(f"Error fetching donors: {e}")
            raise
        finally:
            if conn:
                conn.close()
                
        return donors

    def get_donor_by_id(self, donor_id):
        """Get donor by ID."""
        conn = None
        donor = None
        
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            query = """
            SELECT d.donor_id, d.first_name, d.last_name, d.dob, d.gender,
                   bt.type_name, d.phone_number, d.email, d.address,
                   d.registration_date, d.last_donation_date
            FROM Donors d
            JOIN Blood_Types bt ON d.blood_type_id = bt.blood_type_id
            WHERE d.donor_id = %s;
            """
            
            cur.execute(query, (donor_id,))
            row = cur.fetchone()
            
            if row:
                donor = {
                    "donor_id": row[0],
                    "first_name": row[1],
                    "last_name": row[2],
                    "dob": row[3],
                    "gender": row[4],
                    "blood_type": row[5],
                    "phone_number": row[6],
                    "email": row[7],
                    "address": row[8],
                    "registration_date": row[9],
                    "last_donation_date": row[10]
                }
            
            cur.close()
        except Exception as e:
            print(f"Error fetching donor: {e}")
            raise
        finally:
            if conn:
                conn.close()
                
        return donor

    def search_donors(self, search_term):
        """Search donors by name, email, or phone."""
        conn = None
        donors = []
        
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            search_term = f"%{search_term}%"
            
            query = """
            SELECT d.donor_id, d.first_name, d.last_name, d.dob, d.gender,
                   bt.type_name, d.phone_number, d.email, d.address,
                   d.registration_date, d.last_donation_date
            FROM Donors d
            JOIN Blood_Types bt ON d.blood_type_id = bt.blood_type_id
            WHERE LOWER(d.first_name) LIKE LOWER(%s)
               OR LOWER(d.last_name) LIKE LOWER(%s)
               OR LOWER(d.email) LIKE LOWER(%s)
               OR d.phone_number LIKE %s;
            """
            
            cur.execute(query, (search_term, search_term, search_term, search_term))
            rows = cur.fetchall()
            
            for row in rows:
                donors.append({
                    "donor_id": row[0],
                    "first_name": row[1],
                    "last_name": row[2],
                    "dob": row[3],
                    "gender": row[4],
                    "blood_type": row[5],
                    "phone_number": row[6],
                    "email": row[7],
                    "address": row[8],
                    "registration_date": row[9],
                    "last_donation_date": row[10]
                })
            
            cur.close()
        except Exception as e:
            print(f"Error searching donors: {e}")
            raise
        finally:
            if conn:
                conn.close()
                
        return donors

    def add_donor(self, first_name, last_name, dob, gender, blood_type, phone, email, address):
        """Add a new donor."""
        conn = None
        success = False
        
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            # First get the blood type ID
            cur.execute("SELECT blood_type_id FROM Blood_Types WHERE type_name = %s", (blood_type,))
            blood_type_id = cur.fetchone()
            
            if not blood_type_id:
                raise Exception("Invalid blood type")
                
            blood_type_id = blood_type_id[0]
            
            # Insert the donor
            query = """
            INSERT INTO Donors (
                first_name, last_name, dob, gender, blood_type_id,
                phone_number, email, address, registration_date
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_DATE
            ) RETURNING donor_id;
            """
            
            cur.execute(
                query, 
                (first_name, last_name, dob, gender, blood_type_id, phone, email, address)
            )
            
            donor_id = cur.fetchone()[0]
            conn.commit()
            success = True
            
            cur.close()
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error adding donor: {e}")
            raise
        finally:
            if conn:
                conn.close()
                
        return success

    def update_donor(self, donor_id, first_name, last_name, dob, gender, blood_type, phone, email, address, last_donation_date=None):
        """Update an existing donor."""
        conn = None
        success = False
        
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            # First get the blood type ID
            cur.execute("SELECT blood_type_id FROM Blood_Types WHERE type_name = %s", (blood_type,))
            blood_type_id = cur.fetchone()
            
            if not blood_type_id:
                raise Exception("Invalid blood type")
                
            blood_type_id = blood_type_id[0]
            
            # Update the donor
            if last_donation_date:
                # Update with last donation date
                query = """
                UPDATE Donors SET
                    first_name = %s,
                    last_name = %s,
                    dob = %s,
                    gender = %s,
                    blood_type_id = %s,
                    phone_number = %s,
                    email = %s,
                    address = %s,
                    last_donation_date = %s
                WHERE donor_id = %s;
                """
                
                cur.execute(
                    query, 
                    (first_name, last_name, dob, gender, blood_type_id, phone, email, address, last_donation_date, donor_id)
                )
            else:
                # Update without last donation date
                query = """
                UPDATE Donors SET
                    first_name = %s,
                    last_name = %s,
                    dob = %s,
                    gender = %s,
                    blood_type_id = %s,
                    phone_number = %s,
                    email = %s,
                    address = %s
                WHERE donor_id = %s;
                """
                
                cur.execute(
                    query, 
                    (first_name, last_name, dob, gender, blood_type_id, phone, email, address, donor_id)
                )
            
            conn.commit()
            success = True
            
            cur.close()
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error updating donor: {e}")
            raise
        finally:
            if conn:
                conn.close()
                
        return success

    def delete_donor(self, donor_id):
        """Delete a donor."""
        conn = None
        success = False
        
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            # Delete the donor
            query = "DELETE FROM Donors WHERE donor_id = %s;"
            cur.execute(query, (donor_id,))
            
            conn.commit()
            success = True
            
            cur.close()
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error deleting donor: {e}")
            raise
        finally:
            if conn:
                conn.close()
                
        return success