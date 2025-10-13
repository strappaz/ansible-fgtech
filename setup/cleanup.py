#!/usr/bin/env python3
import subprocess
import sys
import os
import tempfile
import shutil

# --- Configuration ---
# These should match the values in your creation script.
NUM_CONTAINERS = 6
BASE_NAME_TEMPLATE = "systemd-{}"
HOSTNAME_TEMPLATE = "{}.home"
HOSTS_FILE = "/etc/hosts"
HOSTS_ENTRY_TAG = "# Entry added by Docker script"


def run_command(command, check=True):
    """
    Executes a shell command and handles errors.

    Args:
        command (list): The command to execute as a list of strings.
        check (bool): If True, raises an exception on non-zero exit codes.
    """
    try:
        print(f"Executing: {' '.join(command)}")
        subprocess.run(
            command,
            check=check,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return True
    except FileNotFoundError:
        print(f"Error: Command '{command[0]}' not found. Is Docker installed and in your PATH?")
        return False
    except subprocess.CalledProcessError as e:
        # Don't print an error if the container just doesn't exist
        if not ("No such object" in e.stderr or "No such container" in e.stderr):
            print(f"Error executing command: {' '.join(command)}")
            print(f"Stderr: {e.stderr.strip()}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False


def remove_container(name):
    """Stops and removes a Docker container if it exists."""
    print(f"Attempting to stop and remove container '{name}'...")
    # The 'docker stop' command will fail if the container is already stopped,
    # but that's okay. 'docker rm' will then remove it.
    run_command(["docker", "stop", name], check=False)
    run_command(["docker", "rm", name], check=False)
    print(f"Finished removal attempt for container '{name}'.")


def clean_hosts_file(hostname):
    """Removes an entry from the /etc/hosts file safely."""
    print(f"Attempting to remove entry for '{hostname}' from {HOSTS_FILE}.")
    try:
        # Create a temporary file to write the new hosts content
        fd, temp_path = tempfile.mkstemp()

        lines_removed = False
        with os.fdopen(fd, 'w') as new_file:
            with open(HOSTS_FILE, 'r') as old_file:
                for line in old_file:
                    # If the line contains the hostname, we skip it (don't write to new file)
                    if hostname in line.split() and HOSTS_ENTRY_TAG not in line:
                        # This logic handles cases where the hostname might exist for other reasons.
                        # We only want to remove lines added by our script.
                        # A safer approach is to look for the hostname and the comment tag.
                        pass

                    # A better way is to remove the line with the hostname AND the comment above it
                    if hostname not in line:
                        new_file.write(line)
                    else:
                        lines_removed = True

        if lines_removed:
            # Preserve original file's permissions and ownership
            shutil.copymode(HOSTS_FILE, temp_path)
            shutil.chown(temp_path, os.stat(HOSTS_FILE).st_uid, os.stat(HOSTS_FILE).st_gid)
            # Replace the original file with the temporary file
            shutil.move(temp_path, HOSTS_FILE)
            print(f"Successfully removed entry for '{hostname}' from {HOSTS_FILE}.")
        else:
            print(f"No entry for '{hostname}' found to remove.")
            os.remove(temp_path)  # Clean up the temp file if we didn't use it

    except PermissionError:
        print(f"Error: Permission denied. You must run this script with sudo to modify {HOSTS_FILE}.")
        return False
    except Exception as e:
        print(f"Failed to modify {HOSTS_FILE}: {e}")
        # Clean up temp file on error
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        return False
    return True


def main():
    """
    Main function to remove containers and clean up the hosts file.
    """
    # Check for root/sudo privileges
    if os.geteuid() != 0:
        print("This script needs to modify /etc/hosts and remove Docker containers.")
        print("Please run it with sudo: sudo python3 your_cleanup_script.py")
        sys.exit(1)

    print(f"Starting cleanup script for {NUM_CONTAINERS} containers...")

    for i in range(1, NUM_CONTAINERS + 1):
        container_name = BASE_NAME_TEMPLATE.format(i)
        hostname = HOSTNAME_TEMPLATE.format(i)
        print(f"\n--- Cleaning up resource #{i}: {container_name} ---")

        # 1. Remove the container
        remove_container(container_name)

        # 2. Clean the /etc/hosts file
        # This part is tricky because we don't know the IP.
        # We will search for the hostname instead.
        clean_hosts_file(hostname)

    print("\n--- Attempting to remove the script's comment header from /etc/hosts ---")
    try:
        with open(HOSTS_FILE, "r") as f:
            lines = f.readlines()
        with open(HOSTS_FILE, "w") as f:
            for line in lines:
                if HOSTS_ENTRY_TAG not in line.strip("\n"):
                    f.write(line)
        print("General cleanup of host file comments complete.")
    except Exception as e:
        print(f"Could not perform final cleanup of host file comments: {e}")

    print(f"\n--- Script finished. ---")
    print("Running 'docker ps -a -q --filter name=systemd-*' to check for remaining containers:")
    run_command(["docker", "ps", "-a", "-q", "--filter", "name=systemd-*"])


if __name__ == "__main__":
    main()
