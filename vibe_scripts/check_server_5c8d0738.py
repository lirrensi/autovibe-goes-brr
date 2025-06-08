import requests
from requests.exceptions import ConnectionError, Timeout, RequestException

"can you check that kind of server is at http://127.0.0.1:51551"

def check_server_type(url):
    """
    Attempts to connect to a given URL and determines the server type
    by inspecting the 'Server' header in the HTTP response.
    """
    print(f"Attempting to connect to {url} to determine server type...")
    try:
        # Set a timeout for the request to prevent hanging indefinitely
        response = requests.head(url, timeout=5) # Using HEAD request for efficiency
        print(f"Successfully connected to {url}.")
        
        # Check if the 'Server' header is present in the response
        if 'Server' in response.headers:
            server_header = response.headers['Server']
            print(f"Server type found: '{server_header}'")
        else:
            print("No 'Server' header found in the HTTP response.")
            print("This might mean the server is configured not to send this header,")
            print("or it's a very minimal server.")

        print(f"HTTP Status Code: {response.status_code}")
        print("Other response headers (for additional clues):")
        for header, value in response.headers.items():
            print(f"  {header}: {value}")

    except ConnectionError:
        print(f"Error: Could not connect to {url}.")
        print("This usually means the server is not running or the address is incorrect.")
        print("Please ensure the server is active and the URL is correct.")
    except Timeout:
        print(f"Error: Connection to {url} timed out.")
        print("The server did not respond within the expected time frame.")
        print("This could indicate network issues or a very slow server.")
    except RequestException as e:
        print(f"An unexpected error occurred: {e}")
        print("Please check your network connection and the URL.")
    except Exception as e:
        print(f"An unhandled error occurred: {e}")

# Define the URL to check
server_url = "http://127.0.0.1:51551"

# Call the function to check the server type
check_server_type(server_url)
