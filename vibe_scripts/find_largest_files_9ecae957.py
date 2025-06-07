import os
from collections import deque
import time

# Configure the root directory to search. It's recommended to start from a high-level drive, e.g., 'C:\\'
# Be aware that searching the entire C: drive can take a very long time and consume significant resources.
# For testing, you might want to set it to a smaller, specific directory like 'C:\\Users\\YourUser\\Downloads'
ROOT_DIRECTORY = 'C:\\'
# Maximum number of largest files to find
TOP_N = 10

def find_largest_files(root_dir, top_n):
    """
    Finds the top N largest files in the specified root directory and its subdirectories.

    Args:
        root_dir (str): The starting directory for the search.
        top_n (int): The number of largest files to find.

    Returns:
        list: A list of tuples, where each tuple contains (file_path, file_size_in_bytes),
              sorted by size in descending order.
    """
    print(f"Searching for the top {top_n} largest files starting from: {root_dir}")
    print("This process might take a long time depending on the size of the directory and file system speed.")
    print("Please be patient...")

    # Use a min-heap (represented by a deque here for simplicity for a fixed small N)
    # to keep track of the top N largest files found so far.
    # Stores (size, path) tuples. Smallest element is at deque[0] by design.
    largest_files = deque()

    start_time = time.time()
    files_processed = 0
    directories_processed = 0
    errors_encountered = 0

    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=True):
        directories_processed += 1
        # Prune directories that are typically large and not relevant, or permission-denied ones.
        # This is a common optimization for Windows systems.
        # Modifying dirnames in-place affects os.walk's branching.
        dirnames[:] = [d for d in dirnames if not d.lower() in [
            'program files', 'program files (x86)', 'windows', 'system volume information',
            'recovery', '$recycle.bin', 'appdata', 'programdata'
        ]]

        for filename in filenames:
            files_processed += 1
            filepath = os.path.join(dirpath, filename)
            try:
                # Get file status, including size
                # Using os.path.getsize directly might be faster as it doesn't need full stat info
                file_size = os.path.getsize(filepath)

                if len(largest_files) < top_n:
                    largest_files.append((file_size, filepath))
                    # Keep the deque sorted by size in ascending order
                    largest_files = deque(sorted(largest_files))
                elif file_size > largest_files[0][0]: # If current file is larger than the smallest in our top N
                    largest_files.popleft() # Remove the smallest
                    largest_files.append((file_size, filepath))
                    # Re-sort to maintain the min-heap property
                    largest_files = deque(sorted(largest_files))

            except FileNotFoundError:
                # File might have been deleted between os.walk finding it and os.path.getsize call
                # print(f"[WARNING] File not found (likely deleted): {filepath}")
                errors_encountered += 1
                continue
            except PermissionError:
                # Often happens with system files or protected directories
                # print(f"[WARNING] Permission denied to access: {filepath}")
                errors_encountered += 1
                continue
            except OSError as e:
                # Catch other OS-related errors (e.g., invalid path)
                # print(f"[ERROR] OS error for {filepath}: {e}")
                errors_encountered += 1
                continue

    end_time = time.time()
    duration = end_time - start_time

    print(f"\nSearch completed in {duration:.2f} seconds.")
    print(f"Processed {files_processed} files and {directories_processed} directories.")
    if errors_encountered > 0:
        print(f"Encountered {errors_encountered} errors (e.g., permission denied, file not found) while processing files.")
    

    # Sort the final list in descending order by size before returning
    sorted_largest_files = sorted(list(largest_files), key=lambda x: x[0], reverse=True)

    return sorted_largest_files

def format_bytes(size):
    """
    Formats a size in bytes to a human-readable string (e.g., KB, MB, GB).
    """
    power = 2**10
    n = 0
    labels = {0: '', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size >= power and n < len(labels) - 1:
        size /= power
        n += 1
    return f"{size:.2f} {labels[n]}"

if __name__ == "__main__":
    print("Starting the largest file search utility.")
    print("Please be aware that this script requires administrative privileges in some directories, and some files might be skipped due to permissions.")
    print(f"The search will start from: {ROOT_DIRECTORY}")
    print(f"It will attempt to find the top {TOP_N} largest files.")
    print("\n--- Running Search ---")

    try:
        largest_files_found = find_largest_files(ROOT_DIRECTORY, TOP_N)

        print("\n--- Top Largest Files Found ---")
        if largest_files_found:
            for i, (size, path) in enumerate(largest_files_found):
                print(f"{i+1}. {format_bytes(size):<10} - {path}")
        else:
            print("No files were found or processed to determine the largest.")

    except Exception as e:
        print(f"An unexpected error occurred during the search: {e}")
        print("Please ensure the ROOT_DIRECTORY is valid and you have sufficient permissions.")
        print("Try running the script as an administrator if direct permissions are an issue.")

    print("\n--- Script Finished ---")
