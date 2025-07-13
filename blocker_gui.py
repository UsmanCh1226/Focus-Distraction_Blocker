# blocker_gui.py
import json
import tkinter as tk
from tkinter import messagebox, ttk
import csv
import matplotlib.pyplot as plt
from focus_core import start_focus_session, cancel_focus_session, run_with_sudo
from focus_scheduler import start_scheduler, load_schedules
from blocker import WEBSITES
from shared import set_timer_cancelled

def update_status(msg, color):
    status_label.config(text=msg, foreground=color)

def start_focus():
    try:
        minutes = int(duration_entry.get())
        if minutes <= 0:
            raise ValueError
        disable_controls()
        start_focus_session(minutes, on_finish_callback=enable_controls, update_status=update_status)
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a positive integer for minutes.")

def stop_timer():
    cancel_focus_session(update_status=update_status)
    enable_controls()

def start_pomodoro():
    from timer import start_pomodoro_timer
    disable_controls()
    def on_pomodoro_end():
        run_with_sudo("unblock", [])
        enable_controls()
        update_status("Pomodoro ended. Websites unblocked.", "green")
    start_pomodoro_timer(25, 5, status_label, on_finish_callback=on_pomodoro_end)

def disable_controls():
    for btn in [start_button, unblock_button, pomodoro_button, settings_button]:
        btn.config(state=tk.DISABLED)

def enable_controls():
    for btn in [start_button, unblock_button, pomodoro_button, settings_button]:
        btn.config(state=tk.NORMAL)

def unblock_now():
    if run_with_sudo("unblock", []):
        update_status("Websites unblocked.", "green")
        enable_controls()

def view_history():
    win = tk.Toplevel(root)
    win.title("Focus History")
    win.geometry("500x300")
    text = tk.Text(win, wrap=tk.NONE)
    text.pack(expand=True, fill=tk.BOTH)
    try:
        with open("focus_history.csv", "r") as f:
            lines = f.readlines()
            if lines:
                text.insert(tk.END, "Start Time\t\t\tEnd Time\t\t\tDuration (min)\n")
                text.insert(tk.END, "-" * 70 + "\n")
                for line in lines:
                    text.insert(tk.END, line)
            else:
                text.insert(tk.END, "No history available.")
    except FileNotFoundError:
        text.insert(tk.END, "No history file found.")

def show_chart():
    focus_time = 0
    try:
        with open("focus_history.csv", "r") as file:
            reader = csv.reader(file)
            for row in reader:
                try:
                    focus_time += int(row[2])
                except (IndexError, ValueError):
                    continue
    except FileNotFoundError:
        messagebox.showinfo("No Data", "No focus history found.")
        return
    distract_time = max(0, 1440 - focus_time)
    plt.pie([focus_time, distract_time], labels=["Focused", "Distracted"], autopct='%1.1f%%')
    plt.title("Focus vs Distraction Time")
    plt.show()

def open_settings():
    win = tk.Toplevel(root)
    win.title("Settings")
    win.geometry("400x300")

    ttk.Label(win, text="Websites to Block (one per line):").pack(anchor='w', padx=10, pady=5)
    entry = tk.Text(win, height=10)

    try:
        with open("custom_websites.txt", "r") as f:
            entry.insert(tk.END, f.read())
    except FileNotFoundError:
        entry.insert(tk.END, "\n".join(WEBSITES))
    entry.pack(padx=10, fill=tk.BOTH, expand=True)

    def save():
        try:
            with open("custom_websites.txt", "w") as f:
                f.write(entry.get("1.0", tk.END).strip())
            messagebox.showinfo("Saved", "Settings saved. Restart app to apply changes.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    ttk.Button(win, text="Save", command=save).pack(pady=10)

def open_scheduler_editor():
    editor = tk.Toplevel(root)
    editor.title("Schedule Editor")
    editor.geometry("450x400")

    schedules = load_schedules()

    schedule_listbox = tk.Listbox(editor)
    schedule_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def refresh_list():
        schedule_listbox.delete(0, tk.END)
        for i, s in enumerate(schedules):
            days = ", ".join(s["days"])
        schedule_listbox.insert(tk.END, f"{i+1}. {days} @ {s['time']} for {s['duration']}min")

    def add_schedule():
        schedule_popup(schedules, refresh_list)

    def delete_selected():
        selected = schedule_listbox.curselection()
        if selected:
            schedules.pop(selected[0])
            save_schedules(schedules)
            refresh_list()

    ttk.Button(editor, text="Add", command=add_schedule).pack(pady=2)
    ttk.Button(editor, text="Delete Selected", command=delete_selected).pack(pady=2)

    refresh_list()

def load_schedules(filename="schedules.json"):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_schedules(schedules, filename="schedules.json"):
    with open(filename, "w") as f:
        json.dump(schedules, f, indent=2)

def schedule_popup(schedules, on_save):
    popup = tk.Toplevel(root)
    popup.title("Add New Schedule")
    popup.geometry("400x300")

    ttk.Label(popup, text="Time (HH:MM):").pack()
    time_entry = ttk.Entry(popup)
    time_entry.pack()

    ttk.Label(popup, text="Duration (minutes):").pack()
    duration_entry = ttk.Entry(popup)
    duration_entry.pack()

    days_vars = {}
    days_frame = ttk.LabelFrame(popup, text="Days")
    days_frame.pack(pady=5)
    for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
        var = tk.BooleanVar()
        cb = ttk.Checkbutton(days_frame, text=day.capitalize(), variable=var)
        cb.pack(anchor='w')
        days_vars[day] = var

    def save():
        try:
            new_schedule = {
                "time": time_entry.get(),
                "duration": int(duration_entry.get()),
                "days": [d for d, v in days_vars.items() if v.get()]
            }
            schedules.append(new_schedule)
            save_schedules(schedules)
            on_save()
            popup.destroy()
        except ValueError:
            messagebox.showerror("Invalid", "Please enter a valid time and duration.")

    ttk.Button(popup, text="Save", command=save).pack(pady=10)


root = tk.Tk()
root.title("Focus & Distraction Blocker")
root.geometry("350x430")

main_frame = ttk.Frame(root, padding=10)
main_frame.pack(expand=True, fill=tk.BOTH)

ttk.Label(main_frame, text="Focus Duration (minutes):").pack(pady=(0, 5))
duration_entry = ttk.Entry(main_frame)
duration_entry.insert(0, "25")
duration_entry.pack(pady=(0, 10))

start_button = ttk.Button(main_frame, text="Start Focus", command=start_focus)
start_button.pack(pady=2)

pomodoro_button = ttk.Button(main_frame, text="Start Pomodoro", command=start_pomodoro)
pomodoro_button.pack(pady=2)

unblock_button = ttk.Button(main_frame, text="Unblock Now", command=unblock_now)
unblock_button.pack(pady=2)

history_button = ttk.Button(main_frame, text="View History", command=view_history)
history_button.pack(pady=2)

chart_button = ttk.Button(main_frame, text="Show Chart", command=show_chart)
chart_button.pack(pady=2)

settings_button = ttk.Button(main_frame, text="Settings", command=open_settings)
settings_button.pack(pady=5)

schedule_button = ttk.Button(main_frame, text="Schedules", command=open_scheduler_editor)
schedule_button.pack(pady=2)

status_label = ttk.Label(main_frame, text="", foreground="green")
status_label.pack(pady=10)

start_scheduler()

root.mainloop()
