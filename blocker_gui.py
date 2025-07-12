import tkinter as tk
from tkinter import messagebox, ttk
import os
import subprocess
import csv
import matplotlib.pyplot as plt
from blocker import WEBSITES, load_websites
from timer import start_focus_timer, start_pomodoro_timer
from shared import timer_cancelled

def run_with_sudo(action, websites):
    helper_path = os.path.abspath("modify_hosts.py")
    cmd = [
        "osascript", "-e",
        f'do shell script "python3 {helper_path} {action} {" ".join(websites)}" with administrator privileges'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("Success:", result.stdout)
            return True
        else:
            print("Error:", result.stderr)
            messagebox.showerror("Error", f"Failed to {action} websites.\n{result.stderr}")
            return False
    except Exception as e:
        messagebox.showerror("Exception", str(e))
        return False

def start_focus():
    try:
        minutes = int(duration_entry.get())
        if minutes <= 0:
            raise ValueError

        current_websites = load_websites()
        if not run_with_sudo("block", current_websites):
            return

        disable_controls()

        def on_focus_end():
            run_with_sudo("unblock", [])
            enable_controls()
            status_label.config(text="Focus session ended. Websites unblocked.", foreground="green")

        start_focus_timer(
            minutes,
            status_label,
            on_finish_callback=on_focus_end,
            websites=current_websites
        )

        status_label.config(text=f"Focus mode ON for {minutes} minutes. Websites blocked.", foreground="green")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a positive integer for minutes.")

def stop_timer():
    from shared import set_timer_cancelled
    set_timer_cancelled(True)
    unblock_now()
    status_label.config(text="Focus session cancelled.")
    enable_controls()

def start_pomodoro():
    disable_controls()

    def on_pomodoro_end():
        run_with_sudo("unblock", [])
        enable_controls()
        status_label.config(text="Pomodoro ended. Websites unblocked.", foreground="green")

    start_pomodoro_timer(25, 5, status_label, on_finish_callback=on_pomodoro_end)

def disable_controls():
    start_button.config(state=tk.DISABLED)
    unblock_button.config(state=tk.DISABLED)
    pomodoro_button.config(state=tk.DISABLED)
    settings_button.config(state=tk.DISABLED)

def enable_controls():
    start_button.config(state=tk.NORMAL)
    unblock_button.config(state=tk.NORMAL)
    pomodoro_button.config(state=tk.NORMAL)
    settings_button.config(state=tk.NORMAL)

def unblock_now():
    if run_with_sudo("unblock", []):
        status_label.config(text="Websites unblocked.", foreground="green")
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
    try:
        with open("focus_history.csv", mode='r') as file:
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
    labels = ["Focused", "Distracted"]
    times = [focus_time, distract_time]

    plt.pie(times, labels=labels, autopct='%1.1f%%')
    plt.title("Focus vs Distraction Time")
    plt.show()

def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("400x300")

    ttk.Label(settings_window, text="Websites to Block (one per line):").pack(anchor='w', padx=10, pady=5)

    websites_entry = tk.Text(settings_window, height=10)
    try:
        with open("custom_websites.txt", "r") as f:
            websites_entry.insert(tk.END, f.read())
    except FileNotFoundError:
        websites_entry.insert(tk.END, "\n".join(WEBSITES))
    websites_entry.pack(padx=10, fill=tk.BOTH, expand=True)

    def save_settings():
        try:
            new_websites = websites_entry.get("1.0", tk.END).strip().splitlines()
            with open("custom_websites.txt", "w") as f:
                for site in new_websites:
                    f.write(site.strip() + "\n")
            messagebox.showinfo("Saved", "Settings saved. Restart the app to apply changes.")
            settings_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    ttk.Button(settings_window, text="Save", command=save_settings).pack(pady=10)

# GUI SETUP
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

status_label = ttk.Label(main_frame, text="", foreground="green")
status_label.pack(pady=10)

root.mainloop()
