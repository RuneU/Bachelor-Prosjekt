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
    
    return pyodbc.connect(conn_str) # Establish and return connection

# Function to fetch data from the Status table
def fetch_status_data():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.Status, s.Lokasjon, s.EvakuertID, e.Fornavn, e.Etternavn
            FROM Status s
            JOIN Evakuerte e ON s.EvakuertID = e.EvakuertID
        """)
        rows = cursor.fetchall()
        
        data = [
            {
                'Status': row[0],
                'Lokasjon': row[1],
                'EvakuertID': row[2],
                'Fornavn': row[3],
                'Etternavn': row[4]
            }
            for row in rows
        ]
        
        print(data)  # Debug print statement to verify the data
        
        return data
    
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

# Function to post new krise to db
def create_krise(status, krise_situasjon_type, krise_navn, lokasjon, tekstboks):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Krise (Status, KriseSituasjonType, KriseNavn, Lokasjon, Tekstboks)
            VALUES (?, ?, ?, ?, ?)
        """, (status, krise_situasjon_type, krise_navn, lokasjon, tekstboks))
        conn.commit()
        return True
    except pyodbc.Error as e:
        print(f"Error creating krise: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Updates Krise table
def update_krise(krise_id, status, krise_type, krise_navn, lokasjon, tekstboks):
    """
    Updates a row in the Krise table.
    :param krise_id: The ID of the Krise to update.
    :param status: The new status.
    :param krise_type: The new KriseSituasjonType.
    :param krise_navn: The new KriseNavn.
    :param lokasjon: The new Lokasjon.
    :param tekstboks: The new Tekstboks.
    :return: True if the update was successful, False otherwise.
    """
    conn = None
    cursor = None
    try:
        conn = connection_def()  # Establish database connection
        cursor = conn.cursor()

        # Query to update the Krise table
        cursor.execute("""
            UPDATE Krise
            SET 
                KriseSituasjonType = ?, 
                KriseNavn = ?, 
                Status = ?, 
                Lokasjon = ?, 
                Tekstboks = ?
            WHERE KriseID = ?
        """, (
            krise_type,
            krise_navn,
            status,
            lokasjon,
            tekstboks,
            krise_id
        ))

        conn.commit()  # Commit the transaction
        return True  # Return True if the update was successful

    except Exception as e:
        print(f"Error updating Krise: {e}")
        conn.rollback()  # Rollback the transaction in case of an error
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
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

def fetch_krise_by_id(krise_id):
    """
    Fetches a single Krise entry by KriseID.
    Returns a dictionary representing the row, or None if not found.
    """
    conn = None
    cursor = None
    try:
        conn = connection_def()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                KriseID, 
                KriseSituasjonType, 
                KriseNavn, 
                Status, 
                Lokasjon, 
                Tekstboks 
            FROM Krise 
            WHERE KriseID = ?
        """, (krise_id,))

        row = cursor.fetchone()
        if row:
            return {
                "KriseID": row[0],
                "KriseSituasjonType": row[1],
                "KriseNavn": row[2],
                "Status": row[3],
                "Lokasjon": row[4],
                "Tekstboks": row[5]
            }
        else:
            return None

    except Exception as e:
        print(f"Error fetching Krise by ID: {e}")
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def count_evakuerte_by_krise(krise_id):
    try:
        conn = connection_def()
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM Evakuerte WHERE KriseID = ?"
        cursor.execute(query, (krise_id,))
        row = cursor.fetchone()
        return row[0] if row else 0
    except Exception as e:
        print(f"Error counting Evakuerte: {e}")
        return 0
    finally:
        if cursor:
            cursor.close()
        if conn:
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

# Finne alle lokasjoner i databasen for å vise i dropdown
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

# Function to get the last inserted ID
def get_last_inserted_id():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT @@IDENTITY AS ID")
        row = cursor.fetchone()
        return row.ID if row else None
    
    except pyodbc.Error as e:
        print(f"An error occurred: {e}")
        return None
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Function to search statuses based on a query
def search_statuses(query):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        search_query = f"""
            SELECT s.Status, s.Lokasjon, s.EvakuertID, e.Fornavn, e.Etternavn
            FROM Status s
            JOIN Evakuerte e ON s.EvakuertID = e.EvakuertID
            WHERE s.Status LIKE ? OR s.Lokasjon LIKE ? OR e.Fornavn LIKE ? OR e.Etternavn LIKE ?
        """
        cursor.execute(search_query, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
        rows = cursor.fetchall()
        data = [
            {
                'Status': row[0],
                'Lokasjon': row[1],
                'EvakuertID': row[2],
                'Fornavn': row[3],
                'Etternavn': row[4]
            }
            for row in rows
        ]
        
        print(data)  # Debug print statement to verify the data
        
        return data
    except pyodbc.Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Example usage of run_query function
# run_query("INSERT INTO Evakuerte (Fornavn) VALUES ('Seb')")  # Add data

# Example usage of run_query function to alter table
# run_query("ALTER TABLE Evakuerte ADD AzureFaceID NVARCHAR(100) NULL, PhotoURL NVARCHAR(500) NULL;") 

# Example usage of run_query function to delete data
# run_query("DELETE FROM Evakuerte WHERE Fornavn = 'Simon'")  # Delete data

# Fetch and print data from the Status table
try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Status")  # SQL query
    rows = cursor.fetchall()
    
    for row in rows:
        print(row)
        
except pyodbc.Error as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()