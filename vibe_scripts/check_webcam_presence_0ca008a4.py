import subprocess
import sys

def check_webcam_windows():
    """
    Checks for the presence of a webcam on Windows using WMIC or PowerShell.
    """
    print("Attempting to detect webcam on Windows...")

    # Attempt using WMIC first
    print("  Trying WMIC (Windows Management Instrumentation Command-line) method...")
    try:
        # WMIC command to list all PNPDevice with a 'Camera' or 'Imaging' in their caption/description
        # Added Imaging devices as some webcams are classified as such.
        wmic_command = [
            "wmic", "path", "Win32_PnPEntity",
            "where", "Caption like '%Camera%' or Description like '%Camera%' or Caption like '%Imaging%' or Description like '%Imaging%'",
            "get", "Caption", "/format:list"
        ]
        # Using subprocess.run for simpler error handling and capturing output
        wmic_process = subprocess.run(wmic_command, capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)

        if wmic_process.returncode == 0:
            if "Caption=" in wmic_process.stdout:
                print("----------------------------------------------------")
                print("Webcam(s) detected via WMIC. Details:")
                for line in wmic_process.stdout.splitlines():
                    if line.startswith("Caption="):
                        print(f"  - {line.split('=', 1)[1].strip()}")
                print("----------------------------------------------------")
                return True
            else:
                print("  No webcam detected via WMIC using 'Camera' or 'Imaging' keywords.")
        else:
            print(f"  WMIC command failed with return code {wmic_process.returncode}.")
            if wmic_process.stderr:
                print(f"  Error details from WMIC: {wmic_process.stderr.strip()}")
            print("  This might indicate an issue with WMIC query or permissions. Trying PowerShell as an alternative.")

    except FileNotFoundError:
        print("  Error: 'wmic' command not found. This script is intended for Windows operating systems.")
    except subprocess.TimeoutExpired:
        print("  Error: WMIC command timed out. It might be taking too long to respond. Trying PowerShell...")
    except Exception as e:
        print(f"  An unexpected error occurred during WMIC check: {e}. Trying PowerShell...")

    # Fallback to PowerShell if WMIC fails or finds nothing
    print("  Trying PowerShell method...")
    try:
        # PowerShell command to get PnPDevice that are webcams or imaging devices
        # This command explicitly filters for categories like 'Image' devices, often including webcams.
        powershell_command = [
            "powershell",
            "-Command",
            "Get-PnpDevice | Where-Object {$_.Class -eq 'Image' -or $_.FriendlyName -like '*Camera*' -or $_.Description -like '*Camera*'} | Select-Object FriendlyName, Name, Status, DeviceId"
        ]
        powershell_process = subprocess.run(
            powershell_command, 
            capture_output=True, 
            text=True, 
            timeout=15, 
            creationflags=subprocess.CREATE_NO_WINDOW,  # Hide PowerShell window
            shell=True # Use shell=True for complex PowerShell commands
        )

        if powershell_process.returncode == 0 and "FriendlyName" in powershell_process.stdout:
            # Filter out lines that are just headers or formatting if necessary
            useful_output_lines = [line.strip() for line in powershell_process.stdout.splitlines() if line.strip() and not line.strip().startswith(('-----', 'FriendlyName'))]
            
            if useful_output_lines:
                print("----------------------------------------------------")
                print("Webcam(s) detected via PowerShell. Details:")
                print(powershell_process.stdout)
                print("----------------------------------------------------")
                return True
            else:
                print("  No webcam detected via PowerShell based on 'Image' class or 'Camera' keywords.")
                return False
        else:
            print(f"  PowerShell command failed with return code {powershell_process.returncode}.")
            if powershell_process.stderr:
                print(f"  Error details from PowerShell: {powershell_process.stderr.strip()}")
            print("  This might indicate PowerShell is not available or the command failed.")
            return False # No webcam found or error

    except FileNotFoundError:
        print("  Error: 'powershell' command not found. Please ensure PowerShell is installed and in your PATH.")
        return False
    except subprocess.TimeoutExpired:
        print("  Error: PowerShell command timed out. It might be taking too long to respond.")
        return False
    except Exception as e:
        print(f"  An unexpected error occurred during PowerShell check: {e}")
        return False

def check_webcam_linux():
    """
    Checks for the presence of a webcam on Linux using v4l2-ctl (if installed) or lsusb.
    """
    print("Attempting to detect webcam on Linux...")
    try:
        # Try v4l2-ctl first as it's more specific
        print("Trying 'v4l2-ctl --list-devices'...")
        v4l2_output = subprocess.run(["v4l2-ctl", "--list-devices"], capture_output=True, text=True, check=False, timeout=10)
        if v4l2_output.returncode == 0 and "/dev/video" in v4l2_output.stdout:
            print("----------------------------------------------------")
            print("Webcam(s) detected via v4l2-ctl:")
            print(v4l2_output.stdout)
            print("----------------------------------------------------")
            return True
        elif v4l2_output.returncode == 127:
            print("'v4l2-ctl' not found. Trying 'lsusb' as an alternative...")
        else:
            print(f"'v4l2-ctl' command failed or found no devices. Output:\n{v4l2_output.stdout}\nError:\n{v4l2_output.stderr}")

        # Fallback to lsusb if v4l2-ctl is not present or doesn't find anything
        print("Trying 'lsusb' for USB devices that might be webcams...")
        lsusb_output = subprocess.run(["lsusb"], capture_output=True, text=True, check=False, timeout=10)
        if lsusb_output.returncode == 0:
            # Common keywords for webcams in lsusb output
            webcam_keywords = ["Webcam", "Camera", "Video", "Imaging", "UVC"]
            found_webcam_lsusb = False
            print("----------------------------------------------------")
            print("Checking 'lsusb' output for webcam keywords...")
            for line in lsusb_output.stdout.splitlines():
                if any(keyword.lower() in line.lower() for keyword in webcam_keywords):
                    print(f"  - Potentially a webcam: {line.strip()}")
                    found_webcam_lsusb = True
            if found_webcam_lsusb:
                print("----------------------------------------------------")
                return True
            else:
                print("No definite webcam found via 'lsusb' keywords. (Note: This method is less reliable).")
                return False
        else:
            print(f"'lsusb' command failed (return code {lsusb_output.returncode}) or not found. Error: {lsusb_output.stderr.strip()}")
            print("Please ensure 'lsusb' is installed and in your PATH.")
            return False
    except FileNotFoundError:
        print("Error: Neither 'v4l2-ctl' nor 'lsusb' commands were found.")
        print("Please install 'v4l2-utils' (for v4l2-ctl) and 'usbutils' (for lsusb) if you expect to have a webcam.")
        return False
    except subprocess.TimeoutExpired:
        print("Error: Command timed out.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while checking for webcam on Linux: {e}")
        return False

def check_webcam_macos():
    """
    Checks for the presence of a webcam on macOS using system_profiler.
    """
    print("Attempting to detect webcam on macOS using 'system_profiler'...")
    try:
        # Command to list USB devices, which includes internal and external webcams
        command = ["system_profiler", "SPUSBDataType"]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(timeout=15)

        if process.returncode == 0:
            found_webcam = False
            print("----------------------------------------------------")
            print("Checking 'system_profiler' output for webcam indicators...")
            # Look for common webcam names or patterns
            if "FaceTime HD Camera" in stdout or "iSight Camera" in stdout or "USB Camera" in stdout or "Webcam" in stdout or "Video Input" in stdout:
                found_webcam = True
                # Print relevant sections for user
                lines = stdout.splitlines()
                for line_num, line in enumerate(lines):
                    if "Camera" in line or "Webcam" in line or "Video Input" in line:
                        # Print this line and potentially a few subsequent indented lines for context
                        print(f"  - {line.strip()}")
                        # Heuristic to capture indented details. This might need refinement.
                        for i in range(1, 10): # Look up to 9 lines ahead for indented details
                            if line_num + i < len(lines):
                                next_line = lines[line_num + i]
                                if next_line.strip() == "": # Stop on empty line
                                    break
                                if next_line.startswith(" ") and not next_line.startswith("  -"): # Check for indentation (2+ spaces)
                                    print(f"    {next_line.strip()}")
                                else:
                                    # Stop if indentation changes or it's a new top-level item
                                    break

            if found_webcam:
                print("Webcam(s) likely detected. More detailed output can be found by running 'system_profiler SPUSBDataType' in terminal.")
                print("----------------------------------------------------")
                return True
            else:
                print("No common webcam names found in system_profiler output.")
                return False
        else:
            print(f"'system_profiler' command failed with return code {process.returncode}.")
            if stderr:
                print(f"Error details: {stderr.strip()}")
            return False
    except FileNotFoundError:
        print("Error: 'system_profiler' command not found. This script is intended for macOS operating systems.")
        return False
    except subprocess.TimeoutExpired:
        print("Error: 'system_profiler' command timed out. It might be taking too long to respond.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while checking for webcam on macOS: {e}")
        return False

def main():
    print("Starting webcam detection script...")
    operating_system = sys.platform

    webcam_present = False

    if operating_system == "win32":
        print(f"Detected OS: Windows ({operating_system})")
        webcam_present = check_webcam_windows()
    elif operating_system.startswith("linux"): # Includes linux2, linux
        print(f"Detected OS: Linux ({operating_system})")
        webcam_present = check_webcam_linux()
    elif operating_system == "darwin":
        print(f"Detected OS: macOS ({operating_system})")
        webcam_present = check_webcam_macos()
    else:
        print(f"Unsupported operating system: {operating_system}")
        print("Cannot automatically check for webcam. Please consult your system documentation.")
        return

    if webcam_present:
        print("\n\nSummary: A webcam was detected on your system. :) ")
    else:
        print("\n\nSummary: No webcam was definitively detected on your system. :( ")
        if operating_system == "win32":
            print("If you have a webcam, please check its drivers, connection, or privacy settings.")
            print("You can also try opening Device Manager, expanding 'Cameras' or 'Imaging devices' category.")
        elif operating_system.startswith("linux"):
            print("If you have a webcam, ensure relevant drivers (e.g., v4l2) are installed and the device is connected.")
            print("Also, check permissions for /dev/video* devices.")
            print("You might try 'sudo apt install v4l2loopback-utils usbutils' for necessary tools.")
        elif operating_system == "darwin":
            print("If you have a webcam, check its connection, privacy settings (System Settings -> Privacy & Security -> Camera), or try restarting.")

if __name__ == "__main__":
    main()
