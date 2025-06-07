import shutil
import sys

def check_disk_space(threshold_percent=10):
    """
    Checks the disk space of all available drives on Windows and reports if
    any drive's free space falls below a specified percentage threshold.

    Args:
        threshold_percent (int): The percentage threshold for free space.
                                 If free space is below this, a warning is issued.
    """
    print("Starting disk space check...")

    if sys.platform != 'win32':
        print("This script is designed for Windows operating systems (win32).")
        print(f"Current OS detected: {sys.platform}. Exiting.")
        return

    # Iterate through possible drive letters A-Z
    drives_checked = 0
    for drive_letter_ord in range(ord('C'), ord('Z') + 1):  # Start from C: as A: and B: are usually floppy drives
        drive_letter = chr(drive_letter_ord)
        path = f"{drive_letter}:\\"
        
        try:
            total, used, free = shutil.disk_usage(path)
            drives_checked += 1

            total_gb = total / (1024**3)
            used_gb = used / (1024**3)
            free_gb = free / (1024**3)
            free_percent = (free / total) * 100

            print(f"\n--- Drive {drive_letter}:\\ ---")
            print(f"Total: {total_gb:.2f} GB")
            print(f"Used: {used_gb:.2f} GB")
            print(f"Free: {free_gb:.2f} GB")
            print(f"Free Percentage: {free_percent:.2f}%")

            if free_percent < threshold_percent:
                print(f"WARNING: Drive {drive_letter}:\\ has less than {threshold_percent}% free space!")
                print("Consider freeing up space on this drive to avoid performance issues or data loss.")
            else:
                print(f"INFO: Drive {drive_letter}:\\ has sufficient free space (above {threshold_percent}%).")

        except FileNotFoundError:
            # This drive letter does not exist or is not ready (e.g., empty DVD drive)
            # print(f"Drive {drive_letter}:\\ not found or not ready. Skipping.")
            pass # Suppress output for non-existent drives
        except Exception as e:
            print(f"An unexpected error occurred while checking drive {drive_letter}:\\: {e}")

    if drives_checked == 0:
        print("No valid drives were found or checked. Please ensure you have accessible disk drives.")
    else:
        print("\nDisk space check completed.")

# --- Main execution ---
if __name__ == "__main__":
    # You can change the threshold here, e.g., to 15%:
    # check_disk_space(threshold_percent=15)
    check_disk_space() # Uses default threshold of 10%