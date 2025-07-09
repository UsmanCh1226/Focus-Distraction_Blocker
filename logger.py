import csv
import json
from datetime import datetime

CSV_PATH = "focus_history.csv"
JSON_PATH = "history.json"

def log_to_csv(start, end, duration):
    with open(CSV_PATH, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([start, end, duration])

def log_to_json(start, end, websites):
    record = {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "blocked_sites": websites
    }

    try:
        with open(JSON_PATH, 'r+') as file:
            data = json.load(file)
            data.append(record)
            file.seek(0)
            json.dump(data, file, indent=4)
    except FileNotFoundError:
        with open(JSON_PATH, 'w') as file:
            json.dump([record], file, indent=4)

    print(f"[JSON] Logged session with {len(websites_blocked)} sites.")
    