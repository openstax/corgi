from datetime import datetime


def validate_datetime(date_text, format="%Y%m%d.%H%M%S"):
    try:
        datetime.strptime(date_text, format)
    except ValueError:
        return False
    return True
