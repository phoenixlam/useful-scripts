import os
import subprocess
from datetime import datetime

# Configuration
FLAG_FILE   = r"D:\VSCodeProjects\useful-scripts\python\reboot_flag.log"
HISTORY_LOG = r"D:\VSCodeProjects\useful-scripts\python\internet_history.log"
PING_HOSTS = ["1.1.1.1", "8.8.8.8"]


def check_internet():
    """Returns True if at least one host is reachable."""
    for host in PING_HOSTS:
        # -n 1: 1 packet, -w 2000: 2000ms timeout
        result = subprocess.run(
            ["ping", "-n", "1", "-w", "2000", host],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            return True
    return False


def log_event(message):
    """Appends an event entry with timestamp to the permanent log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())
    with open(HISTORY_LOG, "a", encoding="utf-8") as f:
        f.write(log_entry)


def main():
    # Ensure the log directory exists
    os.makedirs(os.path.dirname(HISTORY_LOG), exist_ok=True)

    if check_internet():
        # Connection is UP
        if os.path.exists(FLAG_FILE):
            log_event("SUCCESS: Internet restored after a 1st failure alert.")
            os.remove(FLAG_FILE)
        else:
            log_event("OK: Internet connection active.")
    else:
        # Connection is DOWN
        if not os.path.exists(FLAG_FILE):
            # 1st consecutive failure: Set flag, log event, do NOT reboot
            with open(FLAG_FILE, "w", encoding="utf-8") as f:
                f.write("FAIL")
            log_event("WARNING: 1st internet failure detected. Flag set.")
        else:
            # 2nd consecutive failure: Log event, clear flag, reboot
            log_event("CRITICAL: 2nd consecutive failure detected! Triggering reboot.")
            os.remove(FLAG_FILE)

            # /r = reboot, /f = force close apps, /t 0 = immediate
            subprocess.run(["shutdown", "/r", "/f", "/t", "0"])


if __name__ == "__main__":
    main()
