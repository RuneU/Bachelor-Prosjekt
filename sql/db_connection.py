from dotenv import load_dotenv
import os
import pyodbc

# Load environment variables from .env file
load_dotenv()

# Convert db_config dictionary to a connection string
connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=.database.windows.net;"
    "DATABASE=;"
    "UID=;"
    "PWD=;"
    # "Encrypt=yes;"  # Required for Azure, optional for on-premises
    # "TrustServerCertificate=yes;"  # Only for testing environments
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

# run_query("INSERT INTO Evakuerte (Fornavn) VALUES ('Seb')")  # Add data

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