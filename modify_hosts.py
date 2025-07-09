import sys
import os

HOSTS_PATH = "/etc/hosts"
REDIRECT_IP = "127.0.0.1"
BLOCK_TAG = "# Blocked by FocusBlocker"

def block_websites(websites):
    with open(HOSTS_PATH, "r+") as file:
        content = file.readlines()
        file.seek(0)
        for line in content:
            if any(site in line for site in websites):
                # Already blocked, write original content and exit
                file.writelines(content)
                print("Websites already blocked.")
                return
        # Append blocking lines
        file.writelines(content)
        for website in websites:
            file.write(f"{REDIRECT_IP} {website} {BLOCK_TAG}\n")
        print("Websites blocked successfully.")

def unblock_websites():
    with open(HOSTS_PATH, "r+") as file:
        lines = file.readlines()
        file.seek(0)
        for line in lines:
            if BLOCK_TAG not in line:
                file.write(line)
        file.truncate()
        print("Websites unblocked successfully.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: sudo python3 modify_hosts.py [block|unblock] [site1 site2 ...]")
        sys.exit(1)

    action = sys.argv[1].lower()

    if action == "block":
        websites = sys.argv[2:]
        if not websites:
            print("No websites provided to block.")
            sys.exit(1)
        block_websites(websites)
    elif action == "unblock":
        unblock_websites()
    else:
        print("Invalid action. Use 'block' or 'unblock'.")
