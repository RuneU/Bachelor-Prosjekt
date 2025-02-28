from dotenv import load_dotenv
import os
import pyodbc

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

# Function to fetch data from the Status table
def fetch_status_data():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.Status, s.Lokasjon, s.EvakuertID, e.Fornavn, e.Etternavn, e.KriseID
            FROM Status s
            JOIN Evakuerte e ON s.EvakuertID = e.EvakuertID
        """)
        rows = cursor.fetchall()

        return [
            {
                'Status': row[0],
                'Lokasjon': row[1],
                'EvakuertID': row[2],
                'Fornavn': row[3],
                'Etternavn': row[4],
                'KriseID': row[5]
            }
            for row in rows
        ]
    except pyodbc.Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Function to update status data
def update_status(evakuert_id, status, lokasjon):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Status
            SET Status = ?, Lokasjon = ?
            WHERE EvakuertID = ?
        """, (status, lokasjon, evakuert_id))
        conn.commit()
    except pyodbc.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Function to fetch all kriser
def fetch_all_kriser():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT KriseID, KriseNavn FROM Krise")
        rows = cursor.fetchall()
        return [{'KriseID': row[0], 'KriseNavn': row[1]} for row in rows]
    except pyodbc.Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Function to fetch all locations
def fetch_all_locations():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT Lokasjon FROM Krise")
        rows = cursor.fetchall()
        return [{'LokasjonID': index + 1, 'LokasjonNavn': row[0]} for index, row in enumerate(rows)]
    except pyodbc.Error as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Function to fetch all KriseSituasjonType
def fetch_all_krise_situasjon_types():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT KriseSituasjonType FROM Krise WHERE KriseSituasjonType IS NOT NULL")
        rows = cursor.fetchall()
        return [{'KriseSituasjonType': row[0]} for row in rows]
    except pyodbc.Error as e:
        print(f"Error in fetch_all_krise_situasjon_types: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Function to search statuses based on a query and optional KriseID
def search_statuses(query, krise_id=None):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        search_query = """
            SELECT s.Status, s.Lokasjon, s.EvakuertID, e.Fornavn, e.Etternavn, e.KriseID
            FROM Status s
            JOIN Evakuerte e ON s.EvakuertID = e.EvakuertID
            WHERE (s.Status LIKE ? OR s.Lokasjon LIKE ? OR e.Fornavn LIKE ? OR e.Etternavn LIKE ?)
        """
        params = [f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%']

        if krise_id:
            search_query += " AND e.KriseID = ?"
            params.append(krise_id)

        cursor.execute(search_query, params)
        rows = cursor.fetchall()

        return [
            {
                'Status': row[0],
                'Lokasjon': row[1],
                'EvakuertID': row[2],
                'Fornavn': row[3],
                'Etternavn': row[4],
                'KriseID': row[5]
            }
            for row in rows
        ]
    except pyodbc.Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Function to print Evakuerte data only when explicitly called
def print_evakuerte_data():
    """Fetch and print data from the Evakuerte table when explicitly called."""
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

# Uncomment the next line if you want to manually enable debugging prints
# print_evakuerte_data()
