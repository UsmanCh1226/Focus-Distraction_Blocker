# focus_scheduler.py
import schedule
import time
import threading
import json
from focus_core import start_focus_session

def load_schedules(filename="schedules.json"):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def schedule_all():
    schedules = load_schedules()
    for item in schedules:
        days = item["days"]
        time_str = item["time"]
        duration = item["duration"]

        for day in days:
            getattr(schedule.every(), day).at(time_str).do(
                start_focus_session, minutes=duration,
                on_finish_callback=None,
                update_status=lambda msg, color: print(f"[{color.upper()}] {msg}")
            )

def start_scheduler():
    schedule_all()

    def run_loop():
        while True:
            schedule.run_pending()
            time.sleep(1)

    thread = threading.Thread(target=run_loop, daemon=True)
    thread.start()
