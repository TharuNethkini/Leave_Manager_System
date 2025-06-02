import json
from datetime import datetime

class Database:
    # Initialize with the filename of the JSON data store and load existing data
    def __init__(self, filename):
        self.filename = filename
        self.load()

    # Load data from the JSON file; if 'holidays' key is missing, add it and save
    def load(self):
        with open(self.filename, "r") as f:
            self.data = json.load(f)
        if "holidays" not in self.data:
            self.data["holidays"] = []
        self.save()

    # Write the current state of data back to the JSON file with pretty formatting
    def save(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=4)

    # Append a log message to the system log file with a timestamp
    def log_action(self, message):
        with open("system.log", "a") as log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"[{timestamp}] {message}\n")
