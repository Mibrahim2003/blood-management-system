from database.connection import get_connection

class BloodUnitRepository:
    def add_blood_unit(self, donor_id, blood_type_id, collection_date, expiration_date, status, 
                      storage_location=None, volume_ml=450):
        """
        Add a new blood unit to the database.
        
        Args:
            donor_id (int): ID of the donor
            blood_type_id (int): ID of the blood type
            collection_date (str): Date the blood was collected (YYYY-MM-DD)
            expiration_date (str): Date the blood will expire (YYYY-MM-DD)
            status (str): Status of the blood unit (e.g., 'Available', 'Assigned', 'Used')
            storage_location (str, optional): Where the blood unit is stored. Default is None.
            volume_ml (int, optional): Volume of the blood unit in milliliters. Default is 450.
            
        Returns:
            int: The ID of the newly created blood unit, or None if there was an error
        """
        conn = None
        unit_id = None
        
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            # Check if storage_location column exists
            cur.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'blood_units' AND column_name = 'storage_location'
            """)
            has_storage_location = cur.fetchone() is not None
            
            # Check if volume_ml column exists
            cur.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'blood_units' AND column_name = 'volume_ml'
            """)
            has_volume_ml = cur.fetchone() is not None
            
            # Construct the query based on available columns
            if has_storage_location and has_volume_ml:
                query = """
                INSERT INTO Blood_Units 
                (donor_id, blood_type_id, collection_date, expiration_date, status, storage_location, volume_ml)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING unit_id
                """
                params = (donor_id, blood_type_id, collection_date, expiration_date, status, 
                         storage_location, volume_ml)
            elif has_storage_location:
                query = """
                INSERT INTO Blood_Units 
                (donor_id, blood_type_id, collection_date, expiration_date, status, storage_location)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING unit_id
                """
                params = (donor_id, blood_type_id, collection_date, expiration_date, status, 
                         storage_location)
            elif has_volume_ml:
                query = """
                INSERT INTO Blood_Units 
                (donor_id, blood_type_id, collection_date, expiration_date, status, volume_ml)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING unit_id
                """
                params = (donor_id, blood_type_id, collection_date, expiration_date, status, 
                         volume_ml)
            else:
                query = """
                INSERT INTO Blood_Units 
                (donor_id, blood_type_id, collection_date, expiration_date, status)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING unit_id
                """
                params = (donor_id, blood_type_id, collection_date, expiration_date, status)
            
            cur.execute(query, params)
            unit_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
        except Exception as e:
            print(f"Error adding blood unit: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
        
        return unit_id
    
    def get_blood_unit_by_id(self, unit_id):
        """Get a blood unit by its ID."""
        conn = None
        blood_unit = None
        
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            query = """
            SELECT u.unit_id, u.donor_id, u.blood_type_id, bt.type_name, 
                  u.collection_date, u.expiration_date, u.status
            FROM Blood_Units u
            JOIN Blood_Types bt ON u.blood_type_id = bt.blood_type_id
            WHERE u.unit_id = %s
            """
            
            cur.execute(query, (unit_id,))
            row = cur.fetchone()
            
            if row:
                blood_unit = {
                    "unit_id": row[0],
                    "donor_id": row[1],
                    "blood_type_id": row[2],
                    "blood_type": row[3],
                    "collection_date": row[4],
                    "expiration_date": row[5],
                    "status": row[6]
                }
            
            cur.close()
        except Exception as e:
            print(f"Error fetching blood unit: {e}")
            raise
        finally:
            if conn:
                conn.close()
        
        return blood_unit
    
    def get_all_blood_units(self):
        """Get all blood units from the database."""
        conn = None
        blood_units = []
        
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            query = """
            SELECT u.unit_id, u.donor_id, d.first_name, d.last_name, 
                  u.blood_type_id, bt.type_name, 
                  u.collection_date, u.expiration_date, u.status
            FROM Blood_Units u
            JOIN Blood_Types bt ON u.blood_type_id = bt.blood_type_id
            LEFT JOIN Donors d ON u.donor_id = d.donor_id
            ORDER BY u.collection_date DESC
            """
            
            cur.execute(query)
            rows = cur.fetchall()
            
            for row in rows:
                blood_units.append({
                    "unit_id": row[0],
                    "donor_id": row[1],
                    "donor_name": f"{row[2]} {row[3]}",
                    "blood_type_id": row[4],
                    "blood_type": row[5],
                    "collection_date": row[6],
                    "expiration_date": row[7],
                    "status": row[8]
                })
            
            cur.close()
        except Exception as e:
            print(f"Error fetching blood units: {e}")
            raise
        finally:
            if conn:
                conn.close()
        
        return blood_units

    def update_blood_unit_status(self, unit_id, new_status):
        """Update the status of a blood unit."""
        conn = None
        success = False

        try:
            conn = get_connection()
            cur = conn.cursor()

            query = """
            UPDATE Blood_Units
            SET status = %s
            WHERE unit_id = %s
            """

            cur.execute(query, (new_status, unit_id))
            conn.commit()
            success = cur.rowcount > 0
            cur.close()
        except Exception as e:
            print(f"Error updating blood unit status: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

        return success

    def get_available_blood_units_by_type(self, blood_type_id):
        """Get all available blood units with the specified blood type."""
        conn = None
        blood_units = []
        
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            query = """
            SELECT u.unit_id, u.donor_id, d.first_name, d.last_name, 
                  u.blood_type_id, bt.type_name, 
                  u.collection_date, u.expiration_date, u.status
            FROM Blood_Units u
            JOIN Blood_Types bt ON u.blood_type_id = bt.blood_type_id
            LEFT JOIN Donors d ON u.donor_id = d.donor_id
            WHERE u.blood_type_id = %s AND u.status = 'Available'
            ORDER BY u.collection_date ASC
            """
            
            cur.execute(query, (blood_type_id,))
            rows = cur.fetchall()
            
            for row in rows:
                blood_units.append({
                    "unit_id": row[0],
                    "donor_id": row[1],
                    "donor_name": f"{row[2]} {row[3]}" if row[2] and row[3] else "Unknown Donor",
                    "blood_type_id": row[4],
                    "blood_type": row[5],
                    "collection_date": row[6],
                    "expiration_date": row[7],
                    "status": row[8]
                })
            
            cur.close()
        except Exception as e:
            print(f"Error updating blood unit status: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
        
        return blood_units