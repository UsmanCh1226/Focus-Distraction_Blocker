# blocker.py

DEFAULT_WEBSITES = [
    "facebook.com", "www.facebook.com",
    "youtube.com", "www.youtube.com",
    "twitter.com", "www.twitter.com",
    "instagram.com", "www.instagram.com",
    "reddit.com", "www.reddit.com"
]

def load_websites():
    try:
        with open("custom_websites.txt", "r") as f:
            sites = [line.strip() for line in f if line.strip()]
            return sites if sites else DEFAULT_WEBSITES
    except FileNotFoundError:
        return DEFAULT_WEBSITES

WEBSITES = load_websites()

def blocking_websites(websites, host_path="/etc/hosts", redirect_ip="127.0.0.1"):
    with open(host_path, "r+") as file:
        content = file.read()
        for site in websites:
            if site not in content:
                file.write(f"{redirect_ip} {site}\n")

def unblocking_websites(websites, host_path="/etc/hosts"):
    with open(host_path, "r+") as file:
        lines = file.readlines()
        file.seek(0)
        for line in lines:
            if not any(site in line for site in websites):
                file.write(line)
        file.truncate()
