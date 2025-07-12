import subprocess
import os
from tkinter import messagebox

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
        print("Exception:", e)
        messagebox.showerror("Exception", str(e))
        return False
