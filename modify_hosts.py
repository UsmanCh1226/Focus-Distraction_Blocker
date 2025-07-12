import sys

HOSTS_PATH = "/etc/hosts"
REDIRECT_IP = "127.0.0.1"
BLOCK_TAG = "# Blocked by FocusBlocker"

def block_websites(websites):
    with open(HOSTS_PATH, 'r+') as file:
        lines = file.readlines()
        file.seek(0)
        for line in lines:
            if not any(site in line for site in websites):
                file.write(line)
        for site in websites:
            file.write(f"{REDIRECT_IP} {site} {BLOCK_TAG}\n")
        file.truncate()

def unblock_websites():
    with open(HOSTS_PATH, 'r+') as file:
        lines = file.readlines()
        file.seek(0)
        for line in lines:
            if BLOCK_TAG not in line:
                file.write(line)
        file.truncate()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python modify_hosts.py block|unblock [websites...]")
        sys.exit(1)

    action = sys.argv[1]
    websites = sys.argv[2:]

    if action == "block":
        block_websites(websites)
    elif action == "unblock":
        unblock_websites()
    else:
        print("Invalid action. Use 'block' or 'unblock'.")
