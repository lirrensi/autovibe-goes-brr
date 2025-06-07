import sqlite3
import os
import time

DB_FILE = 'db.db'
TABLE_NAME = 'geo_data'

def create_and_populate_db():
    """Creates an SQLite database and populates it with geo_data."""
    print(f"Checking for existing database file: {os.path.abspath(DB_FILE)}")
    if os.path.exists(DB_FILE):
        print(f"Existing database file '{DB_FILE}' found. Deleting...")
        try:
            os.remove(DB_FILE)
            print(f"Successfully deleted '{DB_FILE}'.")
        except OSError as e:
            print(f"Error deleting existing database file: {e}")
            return

    conn = None
    try:
        print(f"Attempting to connect to database: {DB_FILE}")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        print("Successfully connected to the database.")

        # Create table
        print(f"Creating table '{TABLE_NAME}' if it doesn't exist...")
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                lat REAL NOT NULL,
                lon REAL NOT NULL,
                timestamp INTEGER NOT NULL
            )
        ''')
        conn.commit()
        print(f"Table '{TABLE_NAME}' created successfully.")

        # Populate with some sample data
        print(f"Populating table '{TABLE_NAME}' with sample data...")
        sample_data = [
            ('location_a', 34.0522, -118.2437, int(time.time())),
            ('location_b', 40.7128, -74.0060, int(time.time()) - 3600),
            ('location_c', 51.5074, -0.1278, int(time.time()) - 7200)
        ]

        for data in sample_data:
            try:
                cursor.execute(f'''
                    INSERT INTO {TABLE_NAME} (key, lat, lon, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', data)
                print(f"Inserted record: {data}")
            except sqlite3.IntegrityError as e:
                print(f"Error inserting duplicate key '{data[0]}': {e}")
        conn.commit()
        print("Sample data insertion complete.")

        # Verify data
        print(f"Verifying data in '{TABLE_NAME}'...")
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        rows = cursor.fetchall()
        print("\n--- Current Data in Database ---")
        if rows:
            for row in rows:
                print(row)
        else:
            print("No data found in the table.")
        print("--------------------------------")

        print("Database creation and population successful!")

    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    create_and_populate_db()
