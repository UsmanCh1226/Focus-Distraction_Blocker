import time
import platform
import os
import sys


HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts" if os.name == 'nt' else "/etc/hosts"
REDIRECT_IP = "127.0.0.1"
BLOCK_TAG = "# Blocked by FocusBlocker"

WEBSITES= ["www.youtube.com",
                     "facebook.com",
                     "www.netflix.com",
                     "netflix.com"]



def blocking_websites():
    print("Blocking websites...")
    with open(HOSTS_PATH, "r+") as file:
        content = file.read()
        file.seek(0)
        already_blocked = False
        for line in content:
            if any(site in line for site in WEBSITES):
                already_blocked = True
                break

        if already_blocked:
            print("Websites are already blocked.")

        else:
            file.writelines(content)
            for website in WEBSITES:
                file.write(f"{REDIRECT_IP} {website} {BLOCK_TAG}\n")
            print("Websites successfully blocked.")


def unblocking_websites():
    with open(HOSTS_PATH, "r+") as file:
        lines = file.readlines()
        file.seek(0)
        for line in lines:
            if BLOCK_TAG not in line:
                file.write(line)
        file.truncate()
    print("Websites successfully unblocked.")

def focus_timer(minutes):
    print(f"\nFocus mode ON for {minutes} minute(s). Websites blocked.")
    blocking_websites()
    try:
        time.sleep(minutes * 60)
    except KeyboardInterrupt:
        print("\nFocus interrupted early.")
    finally:
        unblocking_websites()
        print("\nFocus session has ended. Websited unblocked.")









if __name__ =="__main__":
    print("Choose an option:")
    print("1. Block websites")
    print("2. Unblock websites")
    print("3. Start Focus Timer")

    choice = input("Type 'block' to block or 'unblock' to unblock websites: ").strip()
    if choice == '1':
        blocking_websites()
    elif choice == '2':
        unblocking_websites()
    elif choice == '3':
        try:
            mins = int(input("Enter focus mode in minutes: ").strip())
            focus_timer(mins)
        except ValueError:
            print("Please enter a valid number.")
    else:
        print("Invalid choice.")





