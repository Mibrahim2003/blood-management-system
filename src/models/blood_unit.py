"""
Blood Unit Model

This module defines the Blood Unit model for the Blood Donation System.
"""

class BloodUnit:
    def __init__(self, unit_id=None, donor_id=None, blood_type_id=None, 
                 collection_date=None, expiration_date=None, status=None):
        self.unit_id = unit_id
        self.donor_id = donor_id
        self.blood_type_id = blood_type_id
        self.collection_date = collection_date
        self.expiration_date = expiration_date
        self.status = status  # Available, Assigned, Used, Expired, etc.
        
    def __str__(self):
        return f"Blood Unit {self.unit_id}: Type={self.blood_type_id}, Status={self.status}"
