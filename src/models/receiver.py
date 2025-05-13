class Receiver:
    def __init__(self, first_name, last_name, dob, gender, blood_type_id, reason_for_transfusion, hospital_name, ward_details, contact_person_name, contact_person_phone):
        self.first_name = first_name
        self.last_name = last_name
        self.dob = dob
        self.gender = gender
        self.blood_type_id = blood_type_id
        self.reason_for_transfusion = reason_for_transfusion
        self.hospital_name = hospital_name
        self.ward_details = ward_details
        self.contact_person_name = contact_person_name
        self.contact_person_phone = contact_person_phone
        self.registration_date = None  # This will be set when the receiver is added to the database

    def __repr__(self):
        return f"<Receiver {self.first_name} {self.last_name}, Blood Type ID: {self.blood_type_id}>"