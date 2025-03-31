from datetime import datetime
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

def update_krise(krise_id, status, krise_type, krise_navn, lokasjon, tekstboks):
    conn = None
    cursor = None
    try:
        conn = connection_def()  # Establish connection
        cursor = conn.cursor()
        
        # If status is "Ferdig", record the current timestamp; otherwise, set to NULL.
        ferdig_timestamp = datetime.now() if status == "Ferdig" else None

        cursor.execute("""
            UPDATE Krise
            SET 
                KriseSituasjonType = ?, 
                KriseNavn = ?, 
                Status = ?, 
                Lokasjon = ?, 
                Tekstboks = ?,
                FerdigTimestamp = ?
            WHERE KriseID = ?
        """, (
            krise_type,
            krise_navn,
            status,
            lokasjon,
            tekstboks,
            ferdig_timestamp,
            krise_id
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating Krise: {e}")
        conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Function to fetch all kriser
def fetch_all_kriser(order_by='new'):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        order_clause = "ORDER BY Opprettet DESC" if order_by == 'new' else "ORDER BY Opprettet ASC"
        query = f"SELECT KriseID, KriseNavn, Status, Opprettet, FerdigTimestamp FROM Krise {order_clause}"
        cursor.execute(query)
        rows = cursor.fetchall()
        return [
            {'KriseID': row[0], 'KriseNavn': row[1], 'Status': row[2], 'Opprettet': row[3], 'FerdigTimestamp': row[4]}
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

def fetch_krise_by_id(krise_id):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        # Include FerdigTimestamp in your SELECT statement
        cursor.execute("""
            SELECT KriseID, KriseSituasjonType, KriseNavn, Status, Lokasjon, Tekstboks, FerdigTimestamp
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
                "Tekstboks": row[5],
                "FerdigTimestamp": row[6]
            }
        else:
            return None
    except pyodbc.Error as e:
        print(f"Error fetching Krise by ID: {e}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
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

def fetch_status_counts_for_krise(krise_id):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        query = """
            SELECT s.Status, COUNT(*) 
            FROM Status s
            JOIN Evakuerte e ON s.EvakuertID = e.EvakuertID
            WHERE e.KriseID = ?
            GROUP BY s.Status
        """
        cursor.execute(query, (krise_id,))
        rows = cursor.fetchall()
        counts = {}
        for row in rows:
            counts[row[0]] = row[1]

        # Calculate the count for statuses that are not "Akutt", "Haster", or "Vanlig"
        other_count = sum(value for key, value in counts.items() if key not in ("Fysisk uskadet", "Akutt", "Haster", "Vanlig", "Livløs"))
        counts["Other"] = other_count

        return counts
    except Exception as e:
        print(f"Error fetching status counts for Krise: {e}")
        return {}
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

# Function to get the last inserted ID
def get_last_inserted_id():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT SCOPE_IDENTITY() AS ID")
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

# Function to search on Krise based on KriseNavn
def search_krise(query, status_filter=None, order_by='new'):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        base_sql = "SELECT KriseID, KriseNavn, Status, Opprettet FROM Krise WHERE 1=1"
        params = []
        if query:
            base_sql += " AND KriseNavn LIKE ?"
            params.append(f'%{query}%')
        if status_filter:
            base_sql += " AND Status = ?"
            params.append(status_filter)
        order_clause = " ORDER BY Opprettet DESC" if order_by == 'new' else " ORDER BY Opprettet ASC"
        final_sql = base_sql + order_clause
        cursor.execute(final_sql, params)
        rows = cursor.fetchall()
        return [
            {'KriseID': row[0], 'KriseNavn': row[1], 'Status': row[2], 'Opprettet': row[3]}
            for row in rows
        ]
    except pyodbc.Error as e:
        print(f"Error in search_krise: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def count_evakuerte_same_location(krise_id, lokasjon):
    """
    Returns the count of evacuees whose status location matches the crisis location.
    """
    conn = connection_def()
    query = """
        SELECT COUNT(*) 
        FROM Evakuerte e
        JOIN Status s ON e.EvakuertID = s.EvakuertID
        WHERE e.KriseID = ? AND s.Lokasjon = ?
    """
    cur = conn.cursor()
    cur.execute(query, (krise_id, lokasjon))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else 0

def count_evakuerte_different_location(krise_id, lokasjon):
    """
    Returns the count of evacuees that are at a different location than the crisis location.
    This is computed by subtracting the count of evacuees on the crisis location from the total evacuees.
    """
    conn = connection_def()
    total_query = "SELECT COUNT(*) FROM Evakuerte WHERE KriseID = ?"
    cur = conn.cursor()
    cur.execute(total_query, (krise_id,))
    total_result = cur.fetchone()
    total_count = total_result[0] if total_result else 0
    conn.close()
    
    same_count = count_evakuerte_same_location(krise_id, lokasjon)
    return total_count - same_count

def fetch_krise_opprettet(krise_id):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT Opprettet FROM Krise WHERE KriseID = ?", (krise_id,))
        row = cursor.fetchone()
        return row.Opprettet if row else None
    except pyodbc.Error as e:
        print(f"An error occurred while fetching Opprettet timestamp: {e}")
        return None
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

def fetch_combined_evakuerte_status():
    """
    Returns a list of dictionaries, each with the full name (combined Fornavn, MellomNavn, Etternavn),
    Status from the Status table, and Lokasjon from the Status table.
    """
    conn = None
    cursor = None
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.Fornavn, e.MellomNavn, e.Etternavn, s.Status, s.Lokasjon
            FROM Status s
            JOIN Evakuerte e ON s.EvakuertID = e.EvakuertID
        """)
        rows = cursor.fetchall()
        result = []
        for row in rows:
            # Combine names, filtering out any None values
            full_name = " ".join(filter(None, [row[0], row[1], row[2]]))
            result.append({
                'FullName': full_name,
                'Status': row[3],
                'Lokasjon': row[4]
            })
        return result
    except pyodbc.Error as e:
        print(f"Error in fetch_combined_evakuerte_status: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def fetch_combined_evakuerte_status_by_krise(krise_id):
    """
    Returns a list of dictionaries for evacuee status (full name, status, lokasjon, evakuert id)
    for a specific KriseID.
    """
    conn = None
    cursor = None
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.Fornavn, e.MellomNavn, e.Etternavn, s.Status, s.Lokasjon, e.EvakuertID
            FROM Status s
            JOIN Evakuerte e ON s.EvakuertID = e.EvakuertID
            WHERE e.KriseID = ?
        """, (krise_id,))
        rows = cursor.fetchall()
        result = []
        for row in rows:
            full_name = " ".join(filter(None, [row[0], row[1], row[2]]))
            result.append({
                'FullName': full_name,
                'Status': row[3],
                'Lokasjon': row[4],
                'EvakuertID': row[5]
            })
        return result
    except pyodbc.Error as e:
        print(f"Error in fetch_combined_evakuerte_status_by_krise: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Uncomment the next line if you want to manually enable debugging prints
# print_evakuerte_data()
