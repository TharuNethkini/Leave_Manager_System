from datetime import datetime

def validate_date(date_str):
    # Attempts to parse the input string into a date using the YYYY-MM-DD format
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        # Returns True if the date is today or in the future; otherwise False
        return date.date() >= datetime.today().date()
    except:
        # Returns False if the input is not a valid date string
        return False
