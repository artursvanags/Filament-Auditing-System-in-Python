import json
import datetime
import os

def log_changes(log_level, func_name, event, details):
    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "level": log_level,
        "function": func_name,
        "event": event,
        "details": details
    }
    with open("log.json", "a") as log_file:
        log_file.write(json.dumps(log_entry) + "\n")

# If log file doesn't exist, create it and log the creation
if not os.path.exists("log.json"):
    with open("log.json", "w") as log_file:
        log_file.write("")
    log_changes("INFO", "log", "Log file created", "Initial log")