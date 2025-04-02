import serial
import time
import json
import re

SERIAL_PORT = "/dev/ttyarduino_gps" 
BAUD_RATE = 9600
LOCATION_FILE = "location.json"

def save_location(lat, lon):
    with open(LOCATION_FILE, "w") as f:
        json.dump({"lat": lat, "lon": lon}, f)
    print(f"📍 Location saved: {lat}, {lon}")

def read_gps_from_arduino():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"🔌 Listening to {SERIAL_PORT}...")
        while True:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            print("📨 ", line)

            match = re.search(r"Latitude:\s*(-?\d+\.\d+)\s*\|\s*Longitude:\s*(-?\d+\.\d+)", line)
            if match:
                lat = float(match.group(1))
                lon = float(match.group(2))
                save_location(lat, lon)
            time.sleep(1)

    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    read_gps_from_arduino()