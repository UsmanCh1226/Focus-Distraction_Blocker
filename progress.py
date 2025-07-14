import json
from datetime import datetime, timedelta

PROGRESS_FILE = "progress.json"

def load_progress():
    try:
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "xp": 0,
            "streak": 0,
            "last_date": None,
            "history": {}
        }

def save_progress(data):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_xp(duration_minutes, category="Focus", note=""):
    progress = load_progress()

    # Determine earned XP based on session duration
    if duration_minutes < 30:
        earned_xp = 10
    elif duration_minutes < 60:
        earned_xp = 25
    else:
        earned_xp = 50

    progress["xp"] += earned_xp

    today = datetime.now().date()
    last_date_str = progress.get("last_date")

    if last_date_str:
        last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
    else:
        last_date = None

    # Update streak logic
    if last_date == today:
        pass  # Same day, do not update streak
    elif last_date == today - timedelta(days=1):
        progress["streak"] += 1
    else:
        progress["streak"] = 1  # Reset streak

    progress["last_date"] = today.strftime("%Y-%m-%d")

    # Initialize history if missing
    if "history" not in progress:
        progress["history"] = {}

    day_key = today.strftime("%Y-%m-%d")
    if day_key not in progress["history"]:
        progress["history"][day_key] = []

    # Append this session's data
    progress["history"][day_key].append({
        "xp": earned_xp,
        "category": category,
        "note": note
    })

    save_progress(progress)

    print(f"Added {earned_xp} XP in category '{category}'. Note: {note}")
