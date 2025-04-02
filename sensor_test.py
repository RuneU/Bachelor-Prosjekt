from pyfingerprint.pyfingerprint import PyFingerprint

try:
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
    if f.verifyPassword():
        print("✅ Fingerprint sensor is working and verified!")
    else:
        print("❌ Password is wrong (sensor responded, but failed)")
except Exception as e:
    print("💥 Error communicating with sensor:", e)
