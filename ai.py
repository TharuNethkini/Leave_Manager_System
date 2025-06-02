from openai import OpenAI
from config import OPENAI_API_KEY
import re
import dateparser
from datetime import datetime, timedelta

# Initialize the OpenAI client using the API key from config
client = OpenAI(api_key=OPENAI_API_KEY)

def is_valid_date(date_obj):
    """
    Check if the given object is a datetime instance and if its date
    is today or in the future.
    """
    if not isinstance(date_obj, datetime):
        return False
    today = datetime.now().date()
    return date_obj.date() >= today

def get_next_weekday(target_day_name):
    """
    Given the name of a weekday (e.g., 'monday'), return the datetime object
    representing the next occurrence of that weekday from today.
    """
    weekdays = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2,
        'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
    }
    target_day_name = target_day_name.lower()
    if target_day_name in weekdays:
        today = datetime.now()
        target = weekdays[target_day_name]
        # Calculate days ahead until the target weekday
        days_ahead = (target - today.weekday() + 7) % 7 or 7
        return today + timedelta(days=days_ahead)
    return None

def extract_intent_entities(user_input: str):
    """
    A rule-based function to extract the user's intent and entities
    from the input text for leave management.
    It identifies intent such as 'request_leave', 'cancel_leave', 'check_balance', 'view_history', or 'unknown'.
    It also extracts entities like leave_type, num_days, and start_date.
    """
    intent = None
    text = user_input.lower()

    # Check for history-related keywords first (more specific)
    if any(kw in text for kw in [
        "history", "show all my previous", "what leaves have i taken",
        "leave record", "display my leave", "past leave", "previous leave request",
        "what is my past leave", "all my previous leave"
    ]):
        intent = "view_history"
    elif "cancel" in text:
        intent = "cancel_leave"
    elif any(kw in text for kw in ["balance", "how many", "do i have", "remaining", "left"]):
        intent = "check_balance"
    elif any(kw in text for kw in ["take", "request", "need", "off", "leave", "days", "day"]):
        intent = "request_leave"
    else:
        intent = "unknown"

    # Mapping of keywords to standardized leave types
    leave_types = {
        "sick": "Sick Leave",
        "annual": "Annual Leave",
        "maternity": "Maternity Leave"
    }
    entities = {}

    # Identify leave type mentioned in the input
    for key, value in leave_types.items():
        if re.search(r'\b' + re.escape(key) + r'\b', text):
            entities["leave_type"] = value
            break

    # Extract number of days requested (first numeric value found)
    days = re.findall(r'\b\d+\b', user_input)
    if days:
        entities["num_days"] = int(days[0])

    date = None
    import dateparser.search

    # Handle relative date phrases explicitly first
    if "day after tomorrow" in text:
        date = datetime.now() + timedelta(days=2)
    elif "tomorrow" in text:
        date = datetime.now() + timedelta(days=1)

    # Check for 'next <weekday>' pattern
    if not date:
        match = re.search(r'next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', text)
        if match:
            date = get_next_weekday(match.group(1))

    # Fallback to dateparser library to find date mentions
    if not date:
        results = dateparser.search.search_dates(
            user_input,
            settings={'PREFER_DATES_FROM': 'future'}
        )
        if results:
            # Pick the first valid future date found
            for _, dt in results:
                if is_valid_date(dt):
                    date = dt
                    break

    # Format the date as YYYY-MM-DD or set None if no date found
    if date:
        entities["start_date"] = date.strftime('%Y-%m-%d')
    else:
        entities["start_date"] = None

    return intent, entities


def process_input(user_input: str, use_openai=True):
    """
    Processes the user input to extract intent and entities.
    If use_openai is True, it sends the input to OpenAI GPT-3.5-turbo model for extraction,
    expecting a JSON response. If AI fails or parsing fails, falls back to rule-based extraction.
    """
    if not use_openai:
        return extract_intent_entities(user_input)

    messages = [
        {"role": "system", "content": "You are an HR assistant helping employees with leave management. Extract the intent and entities (leave_type, num_days, start_date) from the user input. Return them in JSON format with keys 'intent' and 'entities'."},
        {"role": "user", "content": user_input}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        # Get the assistant's reply text
        reply = response.choices[0].message.content

        # Attempt to parse the JSON formatted response from the AI
        import json
        try:
            data = json.loads(reply)
            intent = data.get("intent", "unknown")
            entities = data.get("entities", {})
            return intent, entities
        except json.JSONDecodeError:
            # If JSON parsing fails, warn and fallback to rule-based extraction
            print("[WARNING] Failed to parse JSON from AI response, falling back to rule-based extraction.")
            return extract_intent_entities(user_input)

    except Exception as e:
        # Handle exceptions during AI call, fallback to rule-based
        if "insufficient_quota" not in str(e):
            print(f"[ERROR] AI processing failed: {e}")
        return extract_intent_entities(user_input)
