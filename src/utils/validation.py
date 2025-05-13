"""
Validation utilities for the Blood Donation System.

This module provides functions for validating user input.
"""

def validate_email(email: str) -> bool:
    """Validate email address format"""
    import re
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    import re
    # Remove any spaces or hyphens
    phone = phone.replace(" ", "").replace("-", "")
    # Check if the phone number has a valid format
    pattern = r"^\+?[0-9]{10,15}$"
    return bool(re.match(pattern, phone))

def validate_date(date_str: str) -> bool:
    """Validate date format (YYYY-MM-DD)"""
    import re
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        return False
    
    try:
        from datetime import datetime
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_blood_type(blood_type_id: int) -> bool:
    """Validate blood type ID is within valid range"""
    return 1 <= blood_type_id <= 8  # 8 standard blood types
