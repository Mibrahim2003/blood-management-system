class BloodType:
    def __init__(self, blood_type_id: int, type_name: str):
        self.blood_type_id = blood_type_id
        self.type_name = type_name

    def __repr__(self):
        return f"BloodType(blood_type_id={self.blood_type_id}, type_name='{self.type_name}')"