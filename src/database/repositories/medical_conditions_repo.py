from typing import List, Dict, Any
import psycopg2
from psycopg2 import sql
from src.database.db_config import config

class MedicalConditionsRepo:
    def __init__(self):
        self.connection = None

    def connect(self):
        """Establish a database connection."""
        params = config()
        self.connection = psycopg2.connect(**params)

    def close(self):
        """Close the database connection."""
        if self.connection is not None:
            self.connection.close()

    def get_all_conditions(self) -> List[Dict[str, Any]]:
        """Retrieve all medical conditions."""
        self.connect()
        conditions = []
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM Medical_Conditions;")
                rows = cursor.fetchall()
                for row in rows:
                    conditions.append({
                        'condition_id': row[0],
                        'condition_name': row[1],
                        'description': row[2],
                        'affects_eligibility': row[3]
                    })
        except Exception as e:
            print(f"Error retrieving conditions: {e}")
        finally:
            self.close()
        return conditions

    def add_condition(self, condition_name: str, description: str, affects_eligibility: bool) -> None:
        """Add a new medical condition."""
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    sql.SQL("INSERT INTO Medical_Conditions (condition_name, description, affects_eligibility) VALUES (%s, %s, %s);"),
                    (condition_name, description, affects_eligibility)
                )
                self.connection.commit()
        except Exception as e:
            print(f"Error adding condition: {e}")
            self.connection.rollback()
        finally:
            self.close()

    def update_condition(self, condition_id: int, condition_name: str, description: str, affects_eligibility: bool) -> None:
        """Update an existing medical condition."""
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    sql.SQL("UPDATE Medical_Conditions SET condition_name = %s, description = %s, affects_eligibility = %s WHERE condition_id = %s;"),
                    (condition_name, description, affects_eligibility, condition_id)
                )
                self.connection.commit()
        except Exception as e:
            print(f"Error updating condition: {e}")
            self.connection.rollback()
        finally:
            self.close()

    def delete_condition(self, condition_id: int) -> None:
        """Delete a medical condition."""
        self.connect()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    sql.SQL("DELETE FROM Medical_Conditions WHERE condition_id = %s;"),
                    (condition_id,)
                )
                self.connection.commit()
        except Exception as e:
            print(f"Error deleting condition: {e}")
            self.connection.rollback()
        finally:
            self.close()