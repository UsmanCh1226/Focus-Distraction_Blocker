# focus_core.py
import os
import subprocess
from blocker import load_websites
from timer import start_focus_timer
from shared import set_timer_cancelled

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
            return False
    except Exception as e:
        print("Exception:", e)
        return False

def start_focus_session(minutes, on_finish_callback=None, update_status=None):
    current_websites = load_websites()
    success = run_with_sudo("block", current_websites)
    if not success:
        if update_status:
            update_status("Blocking failed", "red")
        return False

    def on_focus_end():
        run_with_sudo("unblock", [])
        if on_finish_callback:
            on_finish_callback()
        if update_status:
            update_status("Focus session ended. Websites unblocked.", "green")

    start_focus_timer(minutes, update_status, on_finish_callback=on_focus_end, websites=current_websites)
    if update_status:
        update_status(f"Focus mode ON for {minutes} minutes. Websites blocked.", "green")
    return True

def cancel_focus_session(update_status=None):
    set_timer_cancelled(True)
    run_with_sudo("unblock", [])
    if update_status:
        update_status("Focus session cancelled.", "red")
