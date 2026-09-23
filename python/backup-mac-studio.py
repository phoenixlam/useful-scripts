import os
import subprocess
import sys

# TODO add timestamp in logs

# Define source directories and target backup path on your SSD
SOURCES = [
    "/Users/phoenix/Desktop",
    "/Users/phoenix/Documents",
    "/Users/phoenix/Downloads",
    "/Users/phoenix/MEGA",
    "/Users/phoenix/Pictures",
    "/etc/hosts"
]
DESTINATION = "/Volumes/KINGSTON/BackupMacStudio/"

def run_backup():
    # Ensure destination volume exists
    if not os.path.exists(os.path.dirname(DESTINATION)):
        print(f"Error: Destination volume '{DESTINATION}' not found. Is your SSD connected?")
        sys.exit(1)

    os.makedirs(DESTINATION, exist_ok=True)

    for src in SOURCES:
        if not os.path.exists(src):
            print(f"Skipping {src}: Path does not exist.")
            continue

        print(f"\n--- Backing up: {src} ---")
        
        # Construct rsync command
        cmd = [
            "rsync",
            "-av",
            "--delete",
            "--exclude=.DS_Store",          # Exclude Mac temporary Finder files
            "--exclude=Library/Caches",     # Exclude temporary app caches
            "--exclude=*.dmg",                # Exclude disk image files
            src,
            DESTINATION
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"Successfully backed up {src}")
        except subprocess.CalledProcessError as e:
            print(f"Error backing up {src}: {e}")

if __name__ == "__main__":
    run_backup()
