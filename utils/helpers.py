import re

def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None

def is_valid_coordinates(lat, lng):
    try:
        return -90 <= float(lat) <= 90 and -180 <= float(lng) <= 180
    except (ValueError, TypeError): return False