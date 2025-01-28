# kilde: https://www.youtube.com/watch?v=BgkcKCvuCMM&ab_channel=TechwithHitch
# from connection import connection_string
import pyodbc # pip install && https://learn.microsoft.com/en-us/sql/connect/python/pyodbc/step-1-configure-development-environment-for-pyodbc-python-development?view=sql-server-ver16&tabs=windows

# Convert db_config dictionary to a connection string
connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=krisedb.database.windows.net;"
    "DATABASE=krisesdb;"
    "UID=sysadmin;"
    "PWD=NcbbQkB6nej8E8B;"
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

run_query("DELETE FROM Evakuerte WHERE Fornavn = 'Seb'")  # Delete data

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