class Donor:
    def __init__(self, donor_id, first_name, last_name, dob, gender, blood_type_id, phone_number, email, address=None, registration_date=None, last_donation_date=None):
        self.donor_id = donor_id
        self.first_name = first_name
        self.last_name = last_name
        self.dob = dob
        self.gender = gender
        self.blood_type_id = blood_type_id
        self.phone_number = phone_number
        self.email = email
        self.address = address
        self.registration_date = registration_date
        self.last_donation_date = last_donation_date

    def __repr__(self):
        return f"<Donor(donor_id={self.donor_id}, name={self.first_name} {self.last_name}, blood_type_id={self.blood_type_id})>"