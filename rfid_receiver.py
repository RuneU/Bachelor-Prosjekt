import serial
import time

# Serial Port Settings (Adjust for your OS)
SERIAL_PORT = "/dev/ttyACM0"  # For Linux/Raspberry Pi (use "COM3" on Windows)
BAUD_RATE = 9600  # Match Arduino Serial.begin(9600)

# Global variable for Serial connection
ser = None  # Initialize as None

def connect_serial():
    """Attempts to connect to the Arduino serial port."""
    global ser  # Declare before first use
    while True:
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            print(f"✅ Connected to Arduino on {SERIAL_PORT}")
            time.sleep(2)  # Allow time for connection
            return ser
        except serial.SerialException as e:
            print(f"❌ Error connecting to Arduino: {e}, retrying in 5s...")
            time.sleep(5)

# Initialize serial connection at script start
ser = connect_serial()

def get_rfid_uid():
    """Continuously reads RFID UID from Arduino over Serial."""
    global ser  # Ensure we are modifying the global `ser`

    if not ser:
        return None  

    ser.flushInput()  # Clear old data
    print("🔄 Waiting for RFID card... (Scan an RFID card)")

    try:
        while True:
            data = ser.readline().decode("utf-8").strip()  
            if data:
                if "Card UID:" in data:
                    uid = data.replace("Card UID:", "").strip()
                    print(f"✅ RFID UID Received: {uid}")
                    return uid
    except serial.SerialException as e:
        print(f"❌ Serial connection lost: {e}, reconnecting...")
        ser = connect_serial()  # Attempt reconnection
        return None
    except Exception as e:
        print(f"❌ Error reading RFID from Arduino: {e}")
        return None

if __name__ == "__main__":
    while True:
        rfid_uid = get_rfid_uid()
        if rfid_uid:
            print(f"📌 RFID Scanned: {rfid_uid}")
        time.sleep(1)  # Prevent CPU overload

