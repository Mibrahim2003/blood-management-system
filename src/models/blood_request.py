class BloodRequest:
    def __init__(self, request_id, receiver_id, requesting_doctor, blood_type_id, units_required, request_date, priority, status, units_fulfilled):
        self.request_id = request_id
        self.receiver_id = receiver_id
        self.requesting_doctor = requesting_doctor
        self.blood_type_id = blood_type_id
        self.units_required = units_required
        self.request_date = request_date
        self.priority = priority
        self.status = status
        self.units_fulfilled = units_fulfilled

    def __repr__(self):
        return f"<BloodRequest(request_id={self.request_id}, receiver_id={self.receiver_id}, units_required={self.units_required}, status={self.status})>"