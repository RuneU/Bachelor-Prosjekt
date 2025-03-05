import sys
import time
import pyodbc
from datetime import datetime
from sql.db_connection import connection_string

# Check if running on Raspberry Pi
ON_RASPBERRY_PI = "arm" in sys.platform

if ON_RASPBERRY_PI:
    from mfrc522 import SimpleMFRC522
    import RPi.GPIO as GPIO
    MIFAREReader = SimpleMFRC522()
    GPIO.setmode(GPIO.BOARD)
else:
    print("Running in development mode (RFID will be simulated)")
    MIFAREReader = None

# Database connection
def connect_db():
    try:
        conn = pyodbc.connect(connection_string)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def register_user_with_rfid(user_id):
    """Writes user_id to an RFID card"""
    if not user_id:
        return {'error': 'User ID is required'}

    try:
        if ON_RASPBERRY_PI:
            print("Place an RFID card to register...")
            MIFAREReader.write(user_id)
            return {'message': f'Successfully wrote User ID: {user_id} to RFID card'}
        else:
            return {'message': f'Simulated writing of User ID: {user_id} (development mode)'}
    except Exception as e:
        return {'error': str(e)}

def scan_rfid():
    """Scans an RFID card and records entry"""
    if ON_RASPBERRY_PI:
        print("Waiting for RFID card...")
        rfid_uid, text = MIFAREReader.read()
        rfid_uid_str = str(rfid_uid)
    else:
        time.sleep(2)
        rfid_uid_str = "SIMULATED_UID_12345"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    location = "Office"  # Change dynamically per Raspberry Pi site

    user_id = get_user_id_by_rfid(rfid_uid_str)
    if not user_id:
        return {'error': 'RFID card not registered to any user'}

    store_scan_data(rfid_uid_str, user_id, timestamp, location)

    return {
        'uid': rfid_uid_str,
        'user_id': user_id,
        'timestamp': timestamp,
        'location': location,
        'history': get_scan_history(rfid_uid_str)
    }

def get_user_id_by_rfid(uid):
    """Fetch the associated User ID from RFID UID"""
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT UserID FROM Users WHERE UID = ?", (uid,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    return None

def store_scan_data(uid, user_id, timestamp, location):
    """Log scan data and update user location"""
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ScanLogs (UID, UserID, Timestamp, Location) VALUES (?, ?, ?, ?)",
                       (uid, user_id, timestamp, location))
        cursor.execute("UPDATE Users SET LastLocation = ?, LastScanTime = ? WHERE UID = ?",
                       (location, timestamp, uid))
        conn.commit()
        conn.close()

def get_scan_history(uid):
    """Retrieve scan history of an RFID card"""
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT Timestamp, Location FROM ScanLogs WHERE UID = ? ORDER BY Timestamp DESC", (uid,))
        history = cursor.fetchall()
        conn.close()
        return [{'timestamp': row[0], 'location': row[1]} for row in history]
    return []
