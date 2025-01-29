import pyodbc
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Database connection string setup
connection_string = (
    f"DRIVER={os.getenv('DB_DRIVER')};"
    f"SERVER={os.getenv('DB_SERVER')};"
    f"DATABASE={os.getenv('DB_DATABASE')};"
    f"UID={os.getenv('DB_UID')};"
    f"PWD={os.getenv('DB_PWD')};"
)

# Function to fetch the status data
def fetch_status_data():
    try:
        # Connect to the database
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Execute the query to fetch data from the Status table
        cursor.execute("SELECT Status, Lokasjon, EvakuertID FROM Status")

        # Fetch all the rows from the result
        rows = cursor.fetchall()

        # Return the result as a list of dictionaries
        statuses = [
            {'Status': row[0], 'Lokasjon': row[1], 'EvakuertID': row[2]}
            for row in rows
        ]

        return statuses

    except pyodbc.Error as e:
        print(f"Error: {e}")
        return []

    finally:
        if 'conn' in locals():
            conn.close()