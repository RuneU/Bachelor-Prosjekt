import sys
import time
import pyodbc
import serial  
from datetime import datetime
from sql.db_connection import connection_string
from rfid_receiver import get_rfid_uid  
from flask import Flask, Response, request, render_template, jsonify, redirect, url_for, session, send_from_directory
import json


# Configure Serial Communication (Arduino)

SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to Arduino on {SERIAL_PORT}")
except serial.SerialException as e:
    print(f"❌ Error connecting to Arduino: {e}")
    sys.exit(1)

# Database connection
def connect_db():
    try:
        conn = pyodbc.connect(connection_string)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# Register user with RFID
def RFIDregister(evakuert_id, chip_id):
    """Registers RFID ChipID to an Evakuerte."""
    conn = connect_db()
    if not conn:
        return {"error": "Database connection failed"}

    try:
        cursor = conn.cursor()

        # Check if Evakuert ID exists
        cursor.execute("SELECT EvakuertID FROM Evakuerte WHERE EvakuertID = ?", (evakuert_id,))
        if not cursor.fetchone():
            return {"error": "Evakuert ID not found"}

        # Check if the ChipID already exists in the database
        cursor.execute("SELECT EvakuertID FROM RFID WHERE ChipID = ?", (chip_id,))
        existing_rfid = cursor.fetchone()

        if existing_rfid:
            return {"error": "This RFID ChipID is already assigned to another user"}

        # Update ChipID for this EvakuertID
        cursor.execute("UPDATE RFID SET ChipID = ? WHERE EvakuertID = ?", (chip_id, evakuert_id))
        conn.commit()

        return {"message": "RFID ChipID Registered Successfully!", "chip_id": chip_id}

    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

import json
from datetime import datetime

def read_location_from_file():
    try:
        with open("location.json", "r") as f:
            loc = json.load(f)
            location_name = loc.get("location_name")
            if location_name:
                return location_name
    except Exception as e:
        print(f"⚠️ Failed to read location.json: {e}")
    return "Ukjent"



def scan_rfid():
    """Scans an RFID card, links it to an EvakuertID if new, updates location, and logs scans."""
    print("🔄 Scanning RFID card...")

    rfid_uid = get_rfid_uid()  # Get the RFID UID from Arduino
    if not rfid_uid:
        return {"error": "No RFID card detected"}

    print(f"✅ RFID Scanned: {rfid_uid}")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    location = read_location_from_file()

    # Check if RFID UID is already linked to an EvakuertID
    evakuert_id = get_evakuert_id_by_chipid(rfid_uid)

    if evakuert_id:
        # 🧠 Fetch name from database
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT Fornavn, Etternavn FROM Evakuerte WHERE EvakuertID = ?", (evakuert_id,))
        row = cursor.fetchone()
        conn.close()

        fornavn = row[0] if row else "Ukjent"
        etternavn = row[1] if row else ""

        # 📍 Log location update
        log_location_change(evakuert_id, location)

        return {
            "message": "RFID already linked to an evacuee.",
            "rfid_uid": rfid_uid,
            "evakuert_id": evakuert_id,
            "fornavn": fornavn,
            "etternavn": etternavn,
            "location": location,
            "location_history": get_location_history(evakuert_id)
        }

    # RFID is new, check if the user in session already has an RFID
    if "evakuert_id" not in session:
        return {"error": "No EvakuertID found in session. Cannot register RFID."}

    evakuert_id_session = session["evakuert_id"]

    # Check if the EvakuertID already has an RFID assigned
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ChipID FROM RFID WHERE EvakuertID = ?", (evakuert_id_session,))
        existing_rfid = cursor.fetchone()

        if existing_rfid:
            conn.close()
            return {"error": f"Evakuert ID {evakuert_id_session} already has an RFID assigned."}

        # If EvakuertID has no RFID, link the scanned RFID to the user
        cursor.execute("INSERT INTO RFID (ChipID, EvakuertID) VALUES (?, ?)", (rfid_uid, evakuert_id_session))
        conn.commit()
        conn.close()

        return {
            'message': 'RFID registered successfully!',
            'uid': rfid_uid,
            'evakuert_id': evakuert_id_session,
            'timestamp': timestamp,
            'location': location
        }

    return {"error": "Database connection failed. Could not register RFID."}


def get_evakuert_id_by_chipid(chip_id):
    """Fetch the associated Evakuert ID from the database based on RFID ChipID."""
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
    
        cursor.execute("SELECT EvakuertID FROM RFID WHERE ChipID = ?", (chip_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None
    return None



from rfid_receiver import get_rfid_uid  # Import function to read RFID from Arduino

def scan_rfid_with_history():
    """Scans an RFID card using rfid_receiver and retrieves scan history."""
    
    print("🔄 Scanning RFID card...")
    rfid_uid = get_rfid_uid()  # Get the RFID UID from Arduino

    if not rfid_uid:
        return {"error": "No RFID card detected"}

    print(f" RFID Scanned: {rfid_uid}")

    conn = connect_db()
    if not conn:
        return {"error": "Database connection failed"}

    try:
        cursor = conn.cursor()
        
        # Step 1: Check if the RFID ChipID is registered
        cursor.execute("SELECT EvakuertID FROM RFID WHERE ChipID = ?", (rfid_uid,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return {"error": f"RFID {rfid_uid} is not registered to any Evakuert."}

        evakuert_id = row[0]

        # Retrieve scan history for the EvakuertID
        cursor.execute("""
            SELECT L.change_date, L.old_lokasjon, L.new_lokasjon
            FROM Lokasjon_log L
            JOIN Status S ON L.status_id = S.StatusID
            WHERE S.EvakuertID = ?
            ORDER BY L.change_date DESC
        """, (evakuert_id,))
        
        history = cursor.fetchall()
        conn.close()

        # Format the history data
        scan_history = []
        for scan in history:
            scan_history.append({
                "timestamp": scan[0].strftime("%Y-%m-%d %H:%M:%S"),
                "from": scan[1] if scan[1] else "Unknown",
                "to": scan[2] if scan[2] else "Unknown"
            })

        return {
            "message": "RFID Scan History Retrieved Successfully",
            "rfid_uid": rfid_uid,
            "evakuert_id": evakuert_id,
            "scan_history": scan_history
        }

    except Exception as e:
        return {"error": f"Database query error: {e}"}



def get_current_location():
    """Read location from location.json"""
    with open("location.json", "r") as f:
        loc = json.load(f)
    return f"{loc['lat']}, {loc['lon']}"

def connect_db():
    return pyodbc.connect(connection_string)

def get_evakuert_id_by_chipid(chipid):
    """Return EvakuertID from RFID chip"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT EvakuertID FROM RFID WHERE ChipID = ?", (chipid,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def log_location_change(evakuert_id, new_location):
    conn = connect_db()
    cursor = conn.cursor()

    # Check if status exists
    cursor.execute("SELECT Lokasjon, StatusID FROM Status WHERE EvakuertID = ?", (evakuert_id,))
    row = cursor.fetchone()

    if row:
        old_location, status_id = row
    else:
        old_location = "Ukjent"
        cursor.execute("INSERT INTO Status (EvakuertID, Lokasjon, Status) VALUES (?, ?, 'Aktiv')", (evakuert_id, new_location))
        conn.commit()
        cursor.execute("SELECT StatusID FROM Status WHERE EvakuertID = ?", (evakuert_id,))
        status_id = cursor.fetchone()[0]

    # Log location change
    cursor.execute("""
        INSERT INTO Lokasjon_log (status_id, evakuert_id, old_lokasjon, new_lokasjon)
        VALUES (?, ?, ?, ?)
    """, (status_id, evakuert_id, old_location, new_location))

    # Update current status
    cursor.execute("UPDATE Status SET Lokasjon = ? WHERE EvakuertID = ?", (new_location, evakuert_id))

    conn.commit()
    conn.close()

def get_location_history(evakuert_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT CONVERT(VARCHAR, change_date, 120) AS timestamp, old_lokasjon, new_lokasjon
        FROM Lokasjon_log
        WHERE evakuert_id = ?
        ORDER BY change_date DESC
    """, (evakuert_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"timestamp": r[0], "from": r[1], "to": r[2]} for r in rows]

def scan_rfid_with_logging():
    # Fake for now — replace with real serial or scanning logic
    chip_id = "04A1B2C3D4"  # Simulated read
    evakuert_id = get_evakuert_id_by_chipid(chip_id)
    if not evakuert_id:
        return {"error": "RFID not recognized."}

    location = get_current_location()
    log_location_change(evakuert_id, location)
    history = get_location_history(evakuert_id)

    return {
        "rfid_uid": chip_id,
        "evakuert_id": evakuert_id,
        "location": location,
        "location_history": history
    }


if __name__ == "__main__":
    print("Starting RFID Scanner...")
    while True:
        result = scan_rfid()
        print(result)
