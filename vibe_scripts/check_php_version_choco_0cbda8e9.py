import subprocess
import json

def check_php_latest_choco():
    """Checks if PHP is installed and its version using Chocolatey, and attempts to determine if it's the latest."""
    print("Attempting to check PHP version using Chocolatey...")
    try:
        # Check if Chocolatey is installed
        choco_version_command = ["choco", "--version"]
        print(f"Executing command: {' '.join(choco_version_command)}")
        choco_version_process = subprocess.run(choco_version_command, capture_output=True, text=True, check=True)
        print(f"Chocolatey is installed. Version: {choco_version_process.stdout.strip()}\n")

        print("Querying Chocolatey for installed PHP packages...")
        # Use 'choco list --local-only' to find installed php packages
        list_command = ["choco", "list", "php", "--local-only", "--limit-output"]
        print(f"Executing command: {' '.join(list_command)}")
        list_process = subprocess.run(list_command, capture_output=True, text=True, check=True)
        output_lines = list_process.stdout.strip().split('\n')

        installed_php_version = None
        for line in output_lines:
            if line.startswith("php "):
                parts = line.split()
                if len(parts) >= 2:
                    installed_php_version = parts[1]
                    print(f"Found installed PHP via Chocolatey: Version {installed_php_version}")
                    break
        
        if not installed_php_version:
            print("PHP does not appear to be installed via Chocolatey.")
            print("You can install it using: choco install php")
            return

        print(f"Checking available PHP versions from Chocolatey...")
        # Use 'choco search' to find the latest available PHP version
        search_command = ["choco", "search", "php", "--by-id", "--limit-output"]
        print(f"Executing command: {' '.join(search_command)}")
        search_process = subprocess.run(search_command, capture_output=True, text=True, check=True)
        search_output_lines = search_process.stdout.strip().split('\n')

        latest_php_version = None
        for line in search_output_lines:
            if line.startswith("php "):
                parts = line.split()
                if len(parts) >= 2:
                    latest_php_version = parts[1]
                    # Split version by hyphen if it exists (e.g., 8.2.16-snapshot) and take only first part for comparison
                    if '-' in latest_php_version:
                        latest_php_version = latest_php_version.split('-')[0]
                    print(f"Latest PHP version available via Chocolatey: Version {latest_php_version}")
                    break
        
        if latest_php_version:
            # Simple version comparison (not robust for all versioning schemes, but good for common cases)
            print(f"Comparing installed version ({installed_php_version}) with latest available ({latest_php_version})...")
            if installed_php_version == latest_php_version:
                print(f"SUCCESS: You have the latest PHP version ({installed_php_version}) installed via Chocolatey.")
            else:
                print(f"WARNING: You have PHP version {installed_php_version} installed.")
                print(f"The latest available PHP version via Chocolatey is {latest_php_version}.")
                print(f"To upgrade, you can try: choco upgrade php")
        else:
            print("Could not determine the latest PHP version available via Chocolatey.")

    except FileNotFoundError:
        print("ERROR: Chocolatey (choco command) not found.")
        print("Please ensure Chocolatey is installed and added to your system's PATH.")
        print("You can install Chocolatey from https://chocolatey.org/install")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Chocolatey command failed.\nCommand: {e.cmd}\nReturn Code: {e.returncode}\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}")
        print("Please check the error output from Chocolatey.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    check_php_latest_choco()
