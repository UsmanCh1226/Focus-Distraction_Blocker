import time
import threading
from datetime import datetime
from shared import get_timer_cancelled, set_timer_cancelled

def log_focus_session(start, end, duration):
    with open("focus_history.csv", "a") as f:
        f.write(f"{start}\t{end}\t{duration}\n")

def countdown(minutes, label, on_finish_callback=None, websites=None):
    set_timer_cancelled(False)
    seconds = minutes * 60
    start_time = datetime.now()

    def update():
        nonlocal seconds
        while seconds > 0:
            if get_timer_cancelled():
                return
            mins, secs = divmod(seconds, 60)
            label.config(text=f"Remaining: {mins:02}:{secs:02}")
            time.sleep(1)
            seconds -= 1

        end_time = datetime.now()
        duration = (end_time - start_time).seconds // 60
        log_focus_session(start_time.strftime("%Y-%m-%d %H:%M:%S"), end_time.strftime("%Y-%m-%d %H:%M:%S"), duration)

        if on_finish_callback:
            on_finish_callback()

    threading.Thread(target=update, daemon=True).start()

def start_focus_timer(minutes, label, on_finish_callback=None, websites=None):
    countdown(minutes, label, on_finish_callback, websites)

def start_pomodoro_timer(work_minutes, break_minutes, label, on_finish_callback=None):
    def pomodoro():
        set_timer_cancelled(False)

        label.config(text="Pomodoro: Work session started")
        countdown(work_minutes, label)

        time.sleep(work_minutes * 60)
        if get_timer_cancelled():
            return

        label.config(text="Pomodoro: Break time!")
        countdown(break_minutes, label)

        time.sleep(break_minutes * 60)
        if get_timer_cancelled():
            return

        if on_finish_callback:
            on_finish_callback()

    threading.Thread(target=pomodoro, daemon=True).start()
