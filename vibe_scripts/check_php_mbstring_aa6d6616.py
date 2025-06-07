import subprocess
import re
import os

def find_php_ini_path():
    """Finds the php.ini path using `php -i` command."""
    print("Attempting to find php.ini path...")
    try:
        # Execute php -i to get configuration info
        result = subprocess.run(['php', '-i'], capture_output=True, text=True, check=True, encoding='utf-8')
        php_info = result.stdout

        # Use regex to find the loaded configuration file path
        match = re.search(r'Loaded Configuration File => (.*)', php_info)
        if match:
            php_ini_path = match.group(1).strip()
            if os.path.exists(php_ini_path):
                print(f"Found php.ini at: {php_ini_path}")
                return php_ini_path
            else:
                print(f"php.ini path found ({php_ini_path}) but file does not exist. This might be an issue with PHP installation.")
                return None
        else:
            print("Could not find 'Loaded Configuration File' in php -i output.")
            print("Please ensure PHP is installed and callable from your PATH.")
            return None
    except FileNotFoundError:
        print("Error: 'php' command not found. Please ensure PHP is installed and added to your system's PATH.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error running 'php -i': {e}")
        print(f"Stderr: {e.stderr}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while trying to find php.ini: {e}")
        return None

def check_mbstring_enabled(php_ini_path):
    """Checks if mbstring is enabled in the specified php.ini file."""
    if not php_ini_path or not os.path.exists(php_ini_path):
        print("Invalid php.ini path provided. Cannot check mbstring status.")
        return False

    print(f"Checking for mbstring status in {php_ini_path}...")
    try:
        with open(php_ini_path, 'r', encoding='utf-8', errors='ignore') as f:
            php_ini_content = f.read()

        # Regex to find 'extension=mbstring' lines, ignoring comments (;)
        # It also handles potential spaces and case insensitivity (re.IGNORECASE)
        mbstring_regex = re.compile(r'^\s*extension\s*=\s*mbstring(?:\.dll|\.so)?\s*$', re.IGNORECASE | re.MULTILINE)

        # Check if the line exists and is not commented out
        lines = php_ini_content.splitlines()
        for line in lines:
            stripped_line = line.strip()
            if not stripped_line.startswith(';') and not stripped_line.startswith('#'):
                if mbstring_regex.search(line):
                    print("Success: mbstring extension appears to be ENABLED in php.ini.")
                    return True

        print("Information: mbstring extension does NOT appear to be enabled in php.ini.")
        print("Look for a line like 'extension=mbstring.so' (Linux) or 'extension=mbstring.dll' (Windows) and ensure it's uncommented.")
        return False
    except FileNotFoundError:
        print(f"Error: php.ini file not found at {php_ini_path}.\nThis should not happen if path was found correctly.")
        return False
    except PermissionError:
        print(f"Error: Permission denied when trying to read {php_ini_path}.\nPlease run the script with appropriate permissions.")
        return False
    except Exception as e:
        print(f"An error occurred while reading the php.ini file: {e}")
        return False

if __name__ == '__main__':
    print("Starting PHP mbstring check utility...")
    ini_path = find_php_ini_path()
    if ini_path:
        is_enabled = check_mbstring_enabled(ini_path)
        if is_enabled:
            print("\nSummary: mbstring is likely enabled. Restart your web server (Apache/Nginx) or PHP-FPM for changes to take effect if you just modified php.ini.")
        else:
            print("\nSummary: mbstring is likely NOT enabled. You may need to uncomment or add 'extension=mbstring' in your php.ini and restart your web server/PHP-FPM.")
    else:
        print("\nSummary: Could not determine mbstring status because php.ini path could not be found or accessed.")
