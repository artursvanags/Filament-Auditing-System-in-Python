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