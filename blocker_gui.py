import tkinter as tk
from tkinter import messagebox
import os
from blocker import blocking_websites, unblocking_websites, WEBSITES
from timer import start_focus_timer, start_pomodoro_timer
from logger import log_to_csv, log_to_json
from datetime import datetime
import csv
import matplotlib.pyplot as plt
import subprocess


def run_with_sudo(action, websites):
    helper_path = os.path.abspath("modify_hosts.py")

    cmd = [
        "osascript", "-e",
        f'do shell script "python3 {helper_path} {action} {" ".join(websites)}" with administrator privileges'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            #Success
            print("Success:", result.stdout)
        else:
            print("Error:", result.stderr)
            messagebox.showerror("Error", f"Failed to {action} websites.\n{result.stderr}")
            return False
    except Exception as e:
        print("Exception:", e)
        messagebox.showerror("Exception", str(e))
        return False
    


def start_focus():
    try:
        minutes = int(duration_entry.get())
        if minutes <= 0:
            raise ValueError
        start_focus_timer(
            minutes,
            status_label,
            on_finish_callback=enable_controls,
            websites=WEBSITES
        )
        disable_controls()
    except ValueError:
        messagebox.showerror("Invalid Input", "Enter a positive number of minutes.")

def start_pomodoro():
    disable_controls()
    start_pomodoro_timer(25, 5, status_label, enable_controls)

def disable_controls():
    start_button.config(state=tk.DISABLED)
    unblock_button.config(state=tk.DISABLED)
    pomodoro_button.config(state=tk.DISABLED)

def enable_controls():
    start_button.config(state=tk.NORMAL)
    unblock_button.config(state=tk.NORMAL)
    pomodoro_button.config(state=tk.NORMAL)

def unblock_now():
    unblocking_websites()
    status_label.config(text="Websites unblocked manually.")
    enable_controls()

def view_history():
    history_window = tk.Toplevel(root)
    history_window.title("Focus Session History")
    history_window.geometry("500x300")

    text = tk.Text(history_window, wrap=tk.NONE)
    text.pack(expand=True, fill=tk.BOTH)

    try:
        with open("focus_history.csv", mode='r') as file:
            lines = file.readlines()
            if not lines:
                text.insert(tk.END, "No history available.")
            else:
                text.insert(tk.END, "Start Time\t\t\tEnd Time\t\t\tDuration (min)\n")
                text.insert(tk.END, "-" * 70 + "\n")
                for line in lines:
                    text.insert(tk.END, line)
    except FileNotFoundError:
        text.insert(tk.END, "No history file found.")

def show_chart():
    focus_time = 0
    distract_time = 0

    try:
        with open("focus_history.csv", mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                focus_time += int(row[2])
    except:
        pass

    distract_time = 1440 - focus_time

    labels = ["Focused", "Distracted"]
    times = [focus_time, distract_time]

    plt.pie(times, labels=labels, autopct='%1.1f%%')
    plt.title("Focus vs Distraction Time")
    plt.show()


root = tk.Tk()
root.title("Focus & Distraction Blocker")
root.geometry("350x300")

duration_entry = tk.Entry(root)
duration_entry.insert(0, "25")
duration_entry.pack(pady=10)

start_button = tk.Button(root, text="Start Focus", command=start_focus)
start_button.pack(pady=5)

unblock_button = tk.Button(root, text="Unblock Now", command=unblock_now)
unblock_button.pack(pady=5)

pomodoro_button = tk.Button(root, text="Start Pomodoro", command=start_pomodoro)
pomodoro_button.pack(pady=5)

history_button = tk.Button(root, text="View History", command=view_history)
history_button.pack(pady=5)

chart_button = tk.Button(root, text="Show Chart", command=show_chart)
chart_button.pack(pady=5)

status_label = tk.Label(root, text="")
status_label.pack(pady=10)

root.mainloop()
