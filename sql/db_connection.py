from dotenv import load_dotenv
import os
import pyodbc

# Load environment variables from .env file
load_dotenv()

# Convert db_config dictionary to a connection string
connection_string = (
    f"DRIVER={os.getenv('DB_DRIVER')};"
    f"SERVER={os.getenv('DB_SERVER')};"
    f"DATABASE={os.getenv('DB_DATABASE')};"
    f"UID={os.getenv('DB_UID')};"
    f"PWD={os.getenv('DB_PWD')};"
)

# Redigere data i db
def run_query(x):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute(x)  # Use cursor here instead of conn.execute
        conn.commit()  # Ensure the transaction is committed
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# run_query("INSERT INTO Evakuerte (Fornavn) VALUES ('Simon')")  # Add data

# run_query("DELETE FROM Evakuerte WHERE Fornavn = 'Simon'")  # Delete data

# Fetch and print data from the database
try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Evakuerte")
    rows = cursor.fetchall()
    
    for row in rows:
        print(row)
        
except pyodbc.Error as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()