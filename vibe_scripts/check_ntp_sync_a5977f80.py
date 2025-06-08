import subprocess
import sys
import platform

def check_ntp_sync():
    """
    Checks the NTP synchronization status of the system.
    """
    print("Starting NTP synchronization check...")
    system_platform = platform.system()

    if system_platform == "Windows":
        try:
            print("Detecting Windows OS. Checking w32tm status...")
            # On Windows, we use w32tm /query /status to check NTP sync status.
            # The output contains information about the last successful sync and stratum.
            command = ["w32tm", "/query", "/status"]
            process = subprocess.run(command, capture_output=True, text=True, check=True, encoding='latin1')
            output = process.stdout
            print("w32tm /query /status output:\n" + output)

            # Check for specific indicators of synchronization.
            if "Last Successful Sync Time" in output and "Source:" in output:
                print("\n--- NTP Sync Status (Windows) ---")
                print("NTP service seems to be running and has synchronized.")
                print("Look for 'Last Successful Sync Time' and 'Source' in the output above.")
                print("If 'Source' is 'Local CMOS Clock', it might not be syncing with an external NTP server.")
                print("If 'Stratum' is low (e.g., 1-3), it's likely well-synchronized.")
            elif "The Windows Time service is not running." in output:
                print("\nError: The Windows Time service (w32tm) is not running.")
                print("Please start the 'Windows Time' service via services.msc or 'net start w32time'.")
                print("After starting, you might need to force a resync: 'w32tm /resync'.")
            else:
                print("\nWarning: NTP synchronization status on Windows is unclear from the output.")
                print("Please manually review the 'w32tm /query /status' output.")

            # Further check: w32tm /monitor to see peers
            print("\nChecking w32tm /monitor for peer status (may take a moment)...")
            monitor_command = ["w32tm", "/monitor"]
            monitor_process = subprocess.run(monitor_command, capture_output=True, text=True, check=True, encoding='latin1')
            monitor_output = monitor_process.stdout
            print("w32tm /monitor output:\n" + monitor_output)
            if "Stratum: 0" in monitor_output or "Time server is not running" in monitor_output:
                print("Warning: NTP server might not be configured or running correctly.")
                print("Please verify your NTP client settings.")
            elif "Stratum:" in monitor_output:
                print("NTP peers are being monitored. Look for healthy Stratum values.")
            else:
                 print("Could not determine NTP peer status from w32tm /monitor. Review output manually.")

        except subprocess.CalledProcessError as e:
            print(f"Error executing w32tm: {e}\nStderr: {e.stderr}")
            print("This might indicate that the w32tm command is not found or other system issues.")
        except FileNotFoundError:
            print("Error: 'w32tm' command not found. This command is essential on Windows for NTP checks.")
            print("Ensure Windows Time service components are installed correctly.")
        except Exception as e:
            print(f"An unexpected error occurred on Windows: {e}")

    elif system_platform == "Linux":
        try:
            print("Detecting Linux OS. Checking timedatectl status...")
            # For Linux, timedatectl provides a good overview for systemd-based systems.
            timedatectl_command = ["timedatectl"]
            process = subprocess.run(timedatectl_command, capture_output=True, text=True, check=True)
            output = process.stdout
            print("timedatectl output:\n" + output)

            print("\n--- NTP Sync Status (Linux) ---")
            if "NTP enabled: yes" in output:
                print("NTP is enabled in timedatectl.")
            else:
                print("NTP is reported as disabled. Clock might not be syncing.")
                print("To enable: 'sudo timedatectl set-ntp true'")

            if "NTP synchronized: yes" in output:
                print("NTP is reported as synchronized.")
                print("Your system time is likely in sync with NTP servers.")
            elif "NTP synchronized: no" in output:
                print("Warning: NTP is reported as NOT synchronized.")
                print("This could indicate a configuration issue or network problem.")
                print("Consider checking network connectivity to NTP servers, or the NTP service status (e.g., systemctl status systemd-timesyncd or ntp/chrony).")

            # Try different NTP status commands if timedatectl is not enough or not syncing
            print("\nAttempting more detailed NTP status checks (may vary based on configuration)...")
            ntp_commands = [
                ["ntpq", "-p"],       # For NTPd
                ["chronyc", "tracking"] # For Chrony
            ]
            for cmd in ntp_commands:
                try:
                    print(f"Running command: {' '.join(cmd)}")
                    detailed_process = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    print(f"Output for {' '.join(cmd)}:\n" + detailed_process.stdout)
                    if cmd[0] == "ntpq" and "remote" in detailed_process.stdout.lower() and "reach" in detailed_process.stdout.lower():
                        print("NTP peers detected with ntpq. 'reach' column should be non-zero for active sync.")
                    elif cmd[0] == "chronyc" and "Reference ID" in detailed_process.stdout and "Stratum" in detailed_process.stdout:
                        print("Chrony tracking information detected. Check 'Stratum' and 'System time' offset.")
                except subprocess.CalledProcessError as e:
                    print(f"Command '{' '.join(cmd)}' failed or returned error: {e.returncode}\nStderr: {e.stderr.strip()}")
                    print(f"This command might not be installed or the service is not running.")
                except FileNotFoundError:
                    print(f"Command '{cmd[0]}' not found. This NTP client might not be installed.")
                except Exception as e:
                    print(f"An unexpected error occurred with {cmd[0]}: {e}")


        except subprocess.CalledProcessError as e:
            print(f"Error executing timedatectl: {e}\nStderr: {e.stderr}")
            print("This might indicate a problem with systemd-timesyncd or timedatectl utility.")
        except FileNotFoundError:
            print("Error: 'timedatectl' command not found. This command is essential on systemd Linux for NTP checks.")
            print("Ensure systemd-timesyncd or equivalent is set up.")
        except Exception as e:
            print(f"An unexpected error occurred on Linux: {e}")

    elif system_platform == "Darwin": # Mac OS
        try:
            print("Detecting macOS. NTP sync is handled automatically usually.")
            print("Checking system time settings and NTP service status...")
            # macOS handles NTP mostly automatically via system preferences.
            # We can check system clock settings and then attempt to query an NTP server.

            # Check system date and time preferences
            # This command might not be directly useful for sync status, but shows settings.
            print("\n--- NTP Sync Status (macOS) ---")
            print("macOS generally handles NTP synchronization automatically and transparently.")
            print("You can check 'System Settings > General > Date & Time' to see if 'Set time and date automatically' is enabled.")
            print("The system continuously adjusts the clock to NTP servers.")

            # Using sntp to query a specific NTP server or see daemon status
            print("\nAttempting to query a public NTP server (pool.ntp.org) with sntp...")
            sntp_command = ["sntp", "-s", "pool.ntp.org"]
            process = subprocess.run(sntp_command, capture_output=True, text=True, check=False) # Check = False because sntp often returns non-zero on success for some reason
            output = process.stdout
            error_output = process.stderr

            if output:
                print("sntp output:\n" + output)
                if "successful" in output.lower() or "offset" in output.lower():
                    print("sntp successfully queried an NTP server. Look for offset values.")
                    print("A small offset (close to 0) indicates good synchronization.")
                else:
                    print("sntp command ran, but output is inconclusive. Please review manually.")
            if error_output:
                print("sntp error output (might contain useful info even on success):\n" + error_output)
                if "Could not synchronize" in error_output:
                    print("Warning: sntp reported issues connecting or synchronizing with NTP server.")

        except FileNotFoundError:
            print("Error: 'sntp' command not found. Install it if you wish to manually query NTP servers (e.g., via homebrew: 'brew install sntp').")
            print("macOS default time sync still operates using NTP even without sntp.")
        except Exception as e:
            print(f"An unexpected error occurred on macOS: {e}")

    else:
        print(f"Unsupported operating system: {system_platform}")
        print("Please check your system's documentation for NTP synchronization status commands.")

    print("\nNTP synchronization check complete.")
    print("To confirm true synchronization, compare your system's current time with a reliable external time source (e.g., time.gov).")

# Run the check
check_ntp_sync()
