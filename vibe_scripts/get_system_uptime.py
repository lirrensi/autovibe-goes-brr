import subprocess
import re
import datetime

def get_system_uptime():
    """
    Retrieves the system uptime on Windows 11.
    This function executes the 'systeminfo' command and parses its output
    to find the 'System Boot Time'. Then, it calculates the difference
    between the current time and the boot time to determine the uptime.
    """
    print("Attempting to retrieve system uptime...")
    try:
        # Execute the systeminfo command to get system information
        # Using 'chcp 65001 > NUL' to ensure UTF-8 encoding for command output
        # This helps in parsing characters correctly across different locales.
        command = 'chcp 65001 > NUL && systeminfo | findstr /B "System Boot Time"'
        print(f"Executing command: {command}")
        process = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, encoding='utf-8')
        output = process.stdout.strip()
        print(f"Command output: {output}")

        # Regular expression to find the date and time
        # Expects format like 'System Boot Time:          1/1/2023, 12:00:00 AM'
        match = re.search(r'System Boot Time:\s+(\d{1,2}/\d{1,2}/\d{4}), (\d{1,2}:\d{2}:\d{2}) (AM|PM)', output)
        if match:
            boot_date_str = match.group(1)
            boot_time_str = match.group(2)
            ampm = match.group(3)
            boot_datetime_str = f"{boot_date_str} {boot_time_str} {ampm}"

            # Parse the boot time string into a datetime object
            # The format string matches the output format, e.g., '1/1/2023 12:00:00 AM'
            boot_time = datetime.datetime.strptime(boot_datetime_str, '%m/%d/%Y %I:%M:%S %p')
            current_time = datetime.datetime.now()
            uptime_delta = current_time - boot_time

            # Calculate hours, minutes, and seconds
            total_seconds = int(uptime_delta.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            uptime_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            print(f"System was alive for: {uptime_formatted} (HH:MM:SS)")
            return uptime_formatted
        else:
            print("Error: Could not parse 'System Boot Time' from command output.")
            print("Please check the format of 'systeminfo' output on your system.")
            return None

    except FileNotFoundError:
        print("Error: 'systeminfo' command not found.")
        print("This script is intended for Windows operating systems.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Stderr: {e.stderr}")
        print("Failed to retrieve system information. Please ensure you have necessary permissions.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    # Execute the function to get and print the system uptime
    system_uptime = get_system_uptime()
    if system_uptime:
        print(f"Successfully retrieved system uptime.")
    else:
        print("Failed to retrieve system uptime.")
