import pyodbc
from sql.db_connection import connection_string  # make sure this path is correct

def connect_db():
    try:
        conn = pyodbc.connect(connection_string)
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

def check_current_location(evakuert_id):
    conn = connect_db()
    if not conn:
        return

    cursor = conn.cursor()

    # Get current location
    cursor.execute("""
        SELECT Lokasjon, StatusID FROM Status
        WHERE EvakuertID = ?
    """, (evakuert_id,))
    row = cursor.fetchone()

    if row:
        print(f"✅ Current Location for EvakuertID {evakuert_id}: {row[0]}")
        status_id = row[1]
    else:
        print(f"⚠️  No location found for EvakuertID {evakuert_id}")
        return

    # Show location history
    print("\n📜 Location History:")
    cursor.execute("""
        SELECT change_date, old_lokasjon, new_lokasjon
        FROM Lokasjon_log
        WHERE evakuert_id = ?
        ORDER BY change_date DESC
    """, (evakuert_id,))

    history = cursor.fetchall()
    if not history:
        print("No location history found.")
    else:
        for log in history:
            timestamp, old, new = log
            print(f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')}: {old} → {new}")

    conn.close()

# Example: check for evacuee with ID 1
if __name__ == "__main__":
    evakuert_id_to_check = 10  # Change as needed
    check_current_location(evakuert_id_to_check)

