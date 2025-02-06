from dotenv import load_dotenv
import os
import pyodbc

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

# Creates a callable connection function
def connection_def():
    """Returns a new database connection."""
    conn_str = (
        f"DRIVER={os.getenv('DB_DRIVER')};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_DATABASE')};"
        f"UID={os.getenv('DB_UID')};"
        f"PWD={os.getenv('DB_PWD')};"
    )
    
    return pyodbc.connect(conn_str)  # Establish and return connection

# Redigere data i db
# def run_query(x):

# Function to fetch status data
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

# run_query("INSERT INTO Evakuerte (Fornavn) VALUES ('Seb')")  # Add data

# run_query("DELETE FROM Evakuerte WHERE Fornavn = 'Simon'")  # Delete data

# Fetch and print data from the database
try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Evakuerte")  # SQL query
    rows = cursor.fetchall()
    
    for row in rows:
        print(row)
        
except pyodbc.Error as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()