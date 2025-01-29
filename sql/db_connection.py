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
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT Status, Lokasjon, EvakuertID FROM Status")
        rows = cursor.fetchall()
        
        return [{'Status': row[0], 'Lokasjon': row[1], 'EvakuertID': row[2]} for row in rows]
    
    except pyodbc.Error as e:
        print(f"Error: {e}")
        return []
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Function to run an SQL query (e.g., insert, update, delete)
def run_query(query):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
    
    except pyodbc.Error as e:
        print(f"An error occurred: {e}")
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Function to fetch data from the Evakuerte table
def fetch_evakuerte_data():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Evakuerte")
        rows = cursor.fetchall()
        
        return [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
    
    except pyodbc.Error as e:
        print(f"Error: {e}")
        return []
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
