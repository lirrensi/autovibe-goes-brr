import subprocess
import re
import datetime

def get_system_uptime():
    """
    Retrieves the system uptime on Windows.
    This function executes the 'systeminfo' command and parses its output
    to find the 'System Boot Time'. Then, it calculates the difference
    between the current time and the boot time to determine the uptime.
    Handles different date/time formats by trying multiple patterns.
    """
    print("Attempting to retrieve system uptime...")
    try:
        # Execute the systeminfo command to get system information
        # Using 'chcp 65001 > NUL' to ensure UTF-8 encoding for command output
        # This helps in parsing characters correctly across different locales.
        # Only capture the 'System Boot Time' line to avoid clutter.
        command = 'chcp 65001 > NUL && systeminfo | findstr /B "System Boot Time"'
        print(f"Executing command: {command}")
        process = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, encoding='utf-8')
        output = process.stdout.strip()
        print(f"Command output: {output}")

        # Define multiple regex patterns for different date/time formats
        # Pattern 1: MM/DD/YYYY, HH:MM:SS (standard US with comma and space)
        pattern1 = r'System Boot Time:\s+(\d{1,2}/\d{1,2}/\d{4}), (\d{1,2}:\d{2}:\d{2})'
        # Pattern 2: MM/DD/YYYY, HH:MM:SS AM/PM (standard US with AM/PM)
        pattern2 = r'System Boot Time:\s+(\d{1,2}/\d{1,2}/\d{4}), (\d{1,2}:\d{2}:\d{2}) (AM|PM)'
        # Pattern 3: D/M/YYYY, HH:MM:SS (e.g., 6/2/2025, 10:35:01 as seen in logs)
        pattern3 = r'System Boot Time:\s+(\d{1,2}/\d{1,2}/\d{4}), (\d{1,2}:\d{2}:\d{2})'

        boot_time = None
        parsed_format = None

        formats_to_try = [
            (pattern3, '%m/%d/%Y %H:%M:%S'), # For the console log dump format (02/06/2025, 10:35:01)
            (pattern2, '%m/%d/%Y %I:%M:%S %p'), # For standard AM/PM format
            (pattern1, '%m/%d/%Y %H:%M:%S')  # For 24-hour format without AM/PM
        ]

        for pattern, dt_format in formats_to_try:
            match = re.search(pattern, output)
            if match:
                boot_date_str = match.group(1)
                boot_time_str = match.group(2)
                ampm = match.group(3) if len(match.groups()) == 3 else '' # Safely get AM/PM if present

                # Construct the datetime string based on the matched pattern
                if ampm:
                    boot_datetime_str = f"{boot_date_str} {boot_time_str} {ampm}"
                else:
                    boot_datetime_str = f"{boot_date_str} {boot_time_str}"

                try:
                    boot_time = datetime.datetime.strptime(boot_datetime_str, dt_format)
                    parsed_format = dt_format
                    print(f"Successfully parsed boot time with format '{parsed_format}'.")
                    break # Exit loop if parsing is successful
                except ValueError as ve:
                    print(f"Attempted to parse with format '{dt_format}' but failed: {ve}")
                    continue # Try next format
        
        if boot_time:
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
            print("Error: Could not parse 'System Boot Time' from command output with any known format.")
            print("Please check the format of 'systeminfo' output on your system.")
            print(f"Raw output was: '{output}'")
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
