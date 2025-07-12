import csv
import json
from datetime import datetime

def log_to_csv(start_time, end_time, duration):
    with open("focus_history.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            start_time.strftime("%Y-%m-%d %H:%M:%S"),
            end_time.strftime("%Y-%m-%d %H:%M:%S"),
            duration
        ])

def log_to_json(start_time, end_time, duration):
    data = {
        "start": start_time.isoformat(),
        "end": end_time.isoformat(),
        "duration_minutes": duration
    }

    try:
        with open("focus_history.json", "r") as file:
            history = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    history.append(data)

    with open("focus_history.json", "w") as file:
        json.dump(history, file, indent=4)
