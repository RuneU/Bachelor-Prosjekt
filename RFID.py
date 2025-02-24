import sys
import time
import threading

# Check if running on Raspberry Pi
ON_RASPBERRY_PI = "arm" in sys.platform  # Detects if running on Raspberry Pi

if ON_RASPBERRY_PI:
    from mfrc522 import SimpleMFRC522
    import RPi.GPIO as GPIO
    MIFAREReader = SimpleMFRC522()
    GPIO.setmode(GPIO.BOARD)
else:
    print("Running in development mode (RFID will be simulated)")
    MIFAREReader = None  # No actual RFID reader on a laptop

# Store last scanned UID and counter
last_uid = None
scan_counter = 0
latest_scan = {'uid': None, 'user_id': None, 'scan_count': 0}

def rfid_scan_loop():
    """Continuously scans for RFID tags and updates the global variable."""
    global last_uid, scan_counter, latest_scan

    while True:
        try:
            if ON_RASPBERRY_PI:
                print("Waiting for RFID card...")
                rfid_uid, text = MIFAREReader.read()
                rfid_uid_str = str(rfid_uid)
                stored_user_id = text.strip() if text else "No ID Found"
            else:
                # Simulated data for development on a laptop
                time.sleep(5)  # Fake a 5-second delay
                rfid_uid_str = "SIMULATED_UID_12345"
                stored_user_id = "Simulated_User"

            if last_uid != rfid_uid_str:
                scan_counter += 1
                last_uid = rfid_uid_str

            latest_scan = {
                'uid': rfid_uid_str,
                'user_id': stored_user_id,
                'scan_count': scan_counter
            }

            print(f"RFID Card Read: {latest_scan}")
            time.sleep(1)

        except Exception as e:
            print(f"Error reading RFID: {e}")
            time.sleep(2)

def get_latest_scan():
    """Returns the latest scanned RFID data."""
    return latest_scan

def write_rfid(user_id):
    """Writes a user ID to an RFID card."""
    if not user_id:
        return {'error': 'User ID is required'}, 400

    try:
        if ON_RASPBERRY_PI:
            print("Place an RFID card to write...")
            MIFAREReader.write(user_id)
            return {'message': f'Successfully wrote User ID: {user_id} to RFID card'}
        else:
            return {'message': f'Simulated writing of User ID: {user_id} (development mode)'}

    except Exception as e:
        return {'error': str(e)}, 500

def cleanup_gpio():
    """Cleanup GPIO pins on Raspberry Pi."""
    if ON_RASPBERRY_PI:
        GPIO.cleanup()
