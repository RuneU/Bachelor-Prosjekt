import serial
import time

# --- Configuration ---
GPS_PORT = "/dev/ttyUSB1"   # Adjust if needed
GPS_BAUDRATE = 9600

def convert_to_decimal(raw, direction):
    """Convert NMEA lat/lon to decimal degrees."""
    if not raw or direction not in ["N", "S", "E", "W"]:
        return None
    degrees = float(raw[:2 if direction in ["N", "S"] else 3])
    minutes = float(raw[2 if direction in ["N", "S"] else 3:])
    decimal = degrees + minutes / 60
    if direction in ["S", "W"]:
        decimal = -decimal
    return round(decimal, 6)

def wait_for_gps_fix():
    print("📡 Connecting to GPS module...")
    try:
        ser = serial.Serial(GPS_PORT, GPS_BAUDRATE, timeout=1)
        time.sleep(2)  # Let GPS module warm up
    except Exception as e:
        print("❌ Failed to open GPS port:", e)
        return None

    print("🔄 Waiting for GPS fix...")

    while True:
        try:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if line.startswith("$GPGGA") or line.startswith("$GPRMC"):
                parts = line.split(",")
                if len(parts) > 5 and parts[2] and parts[4]:
                    lat = convert_to_decimal(parts[2], parts[3])
                    lon = convert_to_decimal(parts[4], parts[5])
                    if lat is not None and lon is not None:
                        print("✅ GPS fix acquired!")
                        return lat, lon
                else:
                    print("⏳ Still waiting for GPS fix...")
            time.sleep(1)
        except Exception as e:
            print("⚠️  Error reading GPS data:", e)

if __name__ == "__main__":
    location = wait_for_gps_fix()
    if location:
        print(f"\n📍 Final Location: Latitude={location[0]}, Longitude={location[1]}")
    else:
        print("🚫 GPS fix failed.")
