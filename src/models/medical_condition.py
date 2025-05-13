class MedicalCondition:
    def __init__(self, condition_id, condition_name, description, affects_eligibility):
        self.condition_id = condition_id
        self.condition_name = condition_name
        self.description = description
        self.affects_eligibility = affects_eligibility

    def __repr__(self):
        return f"<MedicalCondition(id={self.condition_id}, name={self.condition_name})>"