import threading
from datetime import datetime, timedelta
from logger import log_to_csv, log_to_json
from blocker import blocking_websites, unblocking_websites

def start_focus_timer(duration_minutes, label, on_finish_callback, websites=()):
    total_seconds = duration_minutes * 60
    end_time = datetime.now() + timedelta(seconds=total_seconds)

    def countdown():
        nonlocal total_seconds

        if total_seconds <= 0:
            unblocking_websites()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_to_csv(start_time, now, duration_minutes)
            log_to_json(start_time, now, duration_minutes, websites)
            label.config(text="Focus session ended!")
            if on_finish_callback:
                on_finish_callback()
            return

        mins,secs = divmod(total_seconds, 60)
        label.config(text=f"Focus Time Left: {mins:02d}:{secs:02d}")
        total_seconds -=1
        label.after(1000,countdown)

    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    blocking_websites()
    countdown()

def start_pomodoro_timer(work_minutes, break_minutes, label, on_cycle_end):
    def on_break_end():
        label.config(text="Pomodoro session complete!")
        if on_cycle_end:
            on_cycle_end()

    def start_break():
        label.config(text="Break has started!")
        label.after(1000, lambda: start_focus_timer(work_minutes, label, start_break))




