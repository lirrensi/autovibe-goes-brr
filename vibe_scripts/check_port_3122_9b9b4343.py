import socket

def check_port_availability(port):
    print(f"Checking if port {port} is available...")
    try:
        # Try to create a socket and bind to the port
        # This will fail if the port is already in use
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", port))
            print(f"Port {port} is open and available for use by an application.")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {port} is currently in use by another application. Error: {e}")
        elif "Access denied" in str(e) or "Permission denied" in str(e):
            print(f"Permission denied to bind to port {port}. You might need administrator privileges or the port is reserved. Error: {e}")
        else:
            print(f"An unexpected error occurred while checking port {port}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    port_to_check = 3122
    check_port_availability(port_to_check)
