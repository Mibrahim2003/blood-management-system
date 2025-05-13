"""
Validation utilities for the Blood Donation Management System
"""
import datetime
import re

class DataValidator:
    @staticmethod
    def validate_name(name):
        """Validate that a name contains only letters and spaces."""
        if not name:
            return False, "Name cannot be empty."
        if not name.replace(" ", "").isalpha():
            return False, "Name should contain only letters."
        return True, ""
    
    @staticmethod
    def validate_date_of_birth(dob_str):
        """Validate that a date of birth is in the correct format and is a reasonable date."""
        if not dob_str:
            return False, "Date of birth cannot be empty."
            
        try:
            date_obj = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
            # Check if date is reasonable (not in the future and not too far in the past)
            today = datetime.datetime.now()
            if date_obj > today:
                return False, "Date of birth cannot be in the future."
            elif today.year - date_obj.year > 120:
                return False, "Date of birth is too far in the past."
            return True, ""
        except ValueError:
            return False, "Date must be in YYYY-MM-DD format (YYYY-MM-DD)."
    
    @staticmethod
    def validate_phone_number(phone, country_code="+92"):
        """Validate phone number format for a specific country code."""
        if not phone:
            return False, "Phone number cannot be empty."
            
        # Remove spaces, dashes, and other separators
        clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Check if it starts with the country code and has reasonable length
        if not clean_phone.startswith(country_code):
            return False, f"Phone number should start with {country_code}."
        
        # Check if the rest are digits and the total length is reasonable
        phone_without_code = clean_phone[len(country_code):]
        if not phone_without_code.isdigit():
            return False, "Phone number should contain only digits after country code."
        
        if len(phone_without_code) < 9 or len(phone_without_code) > 10:
            return False, f"Phone number should have 9-10 digits after {country_code}."
            
        return True, ""
    
    @staticmethod
    def validate_email(email):
        """Validate email format."""
        if not email:
            return True, ""  # Email can be optional
            
        # Simple regex pattern for email validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format."
            
        return True, ""
    
    @staticmethod
    def validate_required_field(value, field_name):
        """Validate that a required field is not empty."""
        if not value:
            return False, f"{field_name} is required."
        return True, ""

# Standalone validation functions
def is_valid_integer(value):
    """Check if the value is a valid positive integer."""
    try:
        num = int(value)
        return num > 0
    except (ValueError, TypeError):
        return False

def validate_receiver_data(data):
    """Validate receiver data for all required fields."""
    errors = []
    
    # Check for required fields
    required_fields = [
        "first_name", "last_name", "dob", "gender", "blood_type_id", 
        "reason_for_transfusion", "hospital_name", "contact_person_name", "contact_person_phone"
    ]
    
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"{field.replace('_', ' ').title()} is required")
    
    # Additional validations
    validator = DataValidator()
    
    # Validate names
    if "first_name" in data and data["first_name"]:
        is_valid, message = validator.validate_name(data["first_name"])
        if not is_valid:
            errors.append(f"First name: {message}")
            
    if "last_name" in data and data["last_name"]:
        is_valid, message = validator.validate_name(data["last_name"])
        if not is_valid:
            errors.append(f"Last name: {message}")
    
    # Validate date of birth
    if "dob" in data and data["dob"]:
        is_valid, message = validator.validate_date_of_birth(data["dob"])
        if not is_valid:
            errors.append(f"Date of birth: {message}")
    
    # Validate contact person phone
    if "contact_person_phone" in data and data["contact_person_phone"]:
        is_valid, message = validator.validate_phone_number(data["contact_person_phone"])
        if not is_valid:
            errors.append(f"Contact person phone: {message}")
    
    return errors

def validate_blood_request(data):
    """Validate blood request data."""
    errors = []
    
    # Check for required fields
    required_fields = ["receiver_id", "blood_type_id", "units_required"]
    
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"{field.replace('_', ' ').title()} is required")
    
    # Validate units required is a positive integer
    if "units_required" in data and data["units_required"]:
        if not is_valid_integer(data["units_required"]):
            errors.append("Units required must be a positive integer")
    
    # Validate priority
    if "priority" in data and data["priority"]:
        valid_priorities = ["Low", "Normal", "High", "Critical"]
        if data["priority"] not in valid_priorities:
            errors.append(f"Priority must be one of: {', '.join(valid_priorities)}")
    
    return errors
