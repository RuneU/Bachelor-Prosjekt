from common_imports import *
from face_utils import save_face

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

latest_frame = None

load_dotenv()

from blueprints.registrer.routes import registrer_bp

try:
    from face_utils import generate_frames
except ImportError as e:
    print("Feil ved import av face.py:", e)

app = Flask(__name__)
app.secret_key = 'your-secret-key'

camera = cv2.VideoCapture(0)  

FACES_FOLDER = "static/faces"

load_dotenv()

AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
if AZURE_CONNECTION_STRING is None:
    raise ValueError("AZURE_STORAGE_CONNECTION_STRING is not set. Check your .env file!")

CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")

def get_db_connection():
    """Establish and return a connection using pyodbc (SQL Server)."""
    try:
        conn = pyodbc.connect(
            f"DRIVER={os.getenv('DB_DRIVER')};"
            f"SERVER={os.getenv('DB_SERVER')};"
            f"DATABASE={os.getenv('DB_DATABASE')};"
            f"UID={os.getenv('DB_UID')};"
            f"PWD={os.getenv('DB_PWD')};"
            f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        )
        return conn
    except pyodbc.Error as e:
        print(f"❌ Database connection error: {e}")
        return None
    
@app.route("/")
@app.route("/startID")
def startID():
    return render_template("startID.html")

@app.route("/noID")
def noID():
    return render_template("noID.html")

@app.route("/fingerLogin")
def fingerLogin():
    return render_template("fingerLogin.html")

@app.route("/fingerRegister")
def fingerRegister():
    return render_template("fingerRegister.html")

@app.route("/RFID")
def RFID():
    return render_template("RFID.html")

@app.route("/finish")
def finish():
    return render_template("finish.html")

@app.route("/newuser")
def newuser():
    return render_template("newuser.html")

@app.route("/olduser")
def olduser():
    return render_template("olduser.html")

@app.route("/iot_login")
def iot_login():
    return render_template("iot_login.html")

@app.route('/fingerRegister')
def finger_register_page():
    return render_template("fingerRegister.html")

@app.route('/fingerLogin')
def finger_login_page():
    return render_template("fingerLogin.html")

@app.route("/api/scan_rfid")
def api_scan_rfid():
    result = scan_rfid()  # or scan_rfid_with_logging()
    return jsonify(result)

@app.route("/scan_location")
def scan_location():
    return render_template("scan_location.html")


@app.route('/set_user_id', methods=['POST'])
def set_user_id():
    data = request.json
    if "evakuert_id" not in data or not data["evakuert_id"].isdigit():
        return jsonify({"error": "Invalid Evakuert ID"}), 400
    
    session["evakuert_id"] = int(data["evakuert_id"])
    return jsonify({"message": "Evakuert ID stored successfully"}), 200

@app.route('/iot')
def iot():
    if "evakuert_id" not in session:
        return redirect(url_for("startID"))  # Ensure user has an ID before proceeding
    return render_template("iot.html", evakuert_id=session["evakuert_id"])

@app.route('/capture')
def capture_page():
    if "evakuert_id" not in session:
        return redirect(url_for("startID"))
    return render_template('capture.html', evakuert_id=session["evakuert_id"])

@app.route("/check_session")
def check_session():
    return jsonify({"evakuert_id": session.get("evakuert_id", "No ID in session")})

 # Route for the recognition page
@app.route('/recognition')
def recognition():
     return render_template('recognition.html')

@app.route('/RFIDregister')
def RFIDregister():
    if "evakuert_id" not in session:
        return redirect(url_for("startID"))
    return render_template('RFIDregister.html', evakuert_id=session["evakuert_id"])

@app.route('/scan', methods=['GET'])
def scan():
    result = scan_rfid()
    return render_template('scan.html', scan_result=result)

@app.route("/gps")
def gps_map():
    LOCATION_FILE = "location.json"
    lat, lon = 59.9139, 10.7522  # Default (Oslo)

    try:
        with open(LOCATION_FILE, "r") as f:
            loc = json.load(f)
            lat = loc.get("lat", lat)
            lon = loc.get("lon", lon)
    except Exception as e:
        logger.warning(f"Location load error: {e}")

    return render_template("gps_map.html", lat=lat, lon=lon)


def generate_frames_with_progress():
    global latest_frame

    # Try to open the default camera (index 0)
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        logging.error("🚫 Could not open camera.")
        return

    logging.info("Camera started. Streaming frames...")

    try:
        while True:
            success, frame = camera.read()
            if not success:
                logging.error("⚠️ Failed to read frame from camera.")
                break

            # Save a copy of the latest frame for other routes to access
            latest_frame = frame.copy()

            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            # Yield multipart response
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    finally:
        camera.release()
        logging.info("🛑 Camera released.")



# Route for video feed with progress updates
@app.route('/video_feed')
def video_feed():
    evakuert_id = request.args.get("evakuert_id")  # Get from URL param
    recognition_mode = request.args.get('recognition', default=False, type=bool)
    # Remove the fetching of known faces if they're not used in generate_frames_with_progress
    if recognition_mode:
        return Response(generate_frames_with_progress(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return Response(generate_frames(evakuert_id),
                        mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/progress')
def progress():
    return Response(generate_frames_with_progress(),
                    mimetype='text/event-stream')


@app.route("/update_location", methods=["POST"])
def update_location():
    LOCATION_FILE = "location.json"
    try:
        data = request.get_json()
        lat = float(data["lat"])
        lon = float(data["lon"])

        # Reverse Geocode using Nominatim
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "format": "json",
                "lat": lat,
                "lon": lon,
                "zoom": 18,
                "addressdetails": 1
            },
            headers={"User-Agent": "EvakueringApp"}
        )
        result = response.json()
        address = result.get("address", {})

        # Extract desired parts
        house_number = address.get("house_number", "")
        road = address.get("road", "")
        city = address.get("city") or address.get("town") or address.get("village", "")
        county = address.get("state", "")           # 'Agder' etc.
        postcode = address.get("postcode", "")
        country = address.get("country", "")

        # Combine parts into readable string
        parts = []

        if road:
            street = f"{road} {house_number}".strip()
            parts.append(street)

        if city:
            parts.append(city)

        if county:
            parts.append(county)

        if postcode:
            parts.append(postcode)

        if country:
            parts.append(country)

        location_name = ", ".join(parts)

        if not location_name:
            location_name = f"{lat:.6f}, {lon:.6f}"

        with open(LOCATION_FILE, "w") as f:
            json.dump({
                "lat": lat,
                "lon": lon,
                "location_name": location_name
            }, f)

        return jsonify({"status": "ok", "location_name": location_name})
    
    except Exception as e:
        print("❌ Error updating location:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_user_info', methods=['GET'])
def get_user_info():
    """Fetch user info based on EvakuertID."""
    evakuert_id = request.args.get('evakuert_id')

    if not evakuert_id:
        return jsonify({"error": "Evakuert ID is required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT Fornavn, MellomNavn, Etternavn, Telefonnummer, Adresse
            FROM Evakuerte
            WHERE EvakuertID = ?
        """
        cursor.execute(query, (evakuert_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            user_data = {
                "fornavn": row[0],
                "mellomnavn": row[1] if row[1] else "",
                "etternavn": row[2],
                "telefonnummer": row[3] if row[3] else "",
                "adresse": row[4] if row[4] else "",
            }
            return jsonify(user_data)
        else:
            return jsonify({"error": "User not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/save_photo', methods=['POST'])
def save_photo():
    try:
        data = request.json
        evakuert_id = int(data.get("evakuert_id"))  # Ensure it's an int
        image_data = data.get("image")

        if not evakuert_id or not image_data:
            return jsonify({"error": "Evakuert ID and image are required"}), 400

        # Call the save_face function from face_utils.py
        return save_face(evakuert_id, image_data)

    except Exception as e:
        logger.error(f"Error saving face: {e}")
        return jsonify({"error": str(e)}), 500

def prepare_image(image):
    """Zoom in on the detected face in the image."""
    # Load the pre-trained Haar Cascade classifier for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) > 0:
        (x, y, w, h) = faces[0]

        # Crop the image to focus on the detected face
        image_cropped = image[y:y+h, x:x+w]
        return image_cropped

    # If no face is detected, return the original image
    return image

@app.route('/capture_face', methods=['POST'])
def capture_face():
     global latest_frame
     if latest_frame is None:
         logger.error("No frame available. Is the camera running?")
         return jsonify({"success": False, "message": "No frame available."})
    
     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
     image_path = f"static/captured_face_{timestamp}.jpg"
    
     try:
         cv2.imwrite(image_path, latest_frame)
         logger.debug(f"Face captured and saved as '{image_path}'")
     except Exception as e:
         logger.error(f"Failed to save image: {e}")
         return jsonify({"success": False, "message": "Failed to save image."})
    
     recognized_faces = recognize_faces_from_image(image_path)
    
     if recognized_faces:
         return jsonify({"success": True, "recognized_faces": recognized_faces})
     else:
         return jsonify({"success": False, "message": "No faces recognized."})

def recognize_faces_from_image(image_path):
    known_face_encodings, known_face_ids, known_face_names = fetch_known_faces_from_db()

    image = face.load_image_file(image_path)

    # Detect face locations first
    face_locations = face.face_locations(image)
    print(f"🔍 Detected {len(face_locations)} face(s) in image")

    if not face_locations:
        return []  # No face detected at all

    # Then encode faces at those locations
    captured_encodings = face.face_encodings(image, face_locations)

    recognized_faces = []
    for captured_encoding in captured_encodings:
        best_match_id, best_match_name, distance = find_best_match(
            captured_encoding,
            known_face_encodings,
            known_face_ids,
            known_face_names
        )
        if best_match_id is not None:
            recognized_faces.append({
                "id": best_match_id,
                "name": best_match_name,
                "distance": float(distance)
            })

    return recognized_faces


def fetch_known_faces_from_db():
    
     known_face_encodings = []
     known_face_ids = []
     known_face_names = []
    
    
     try:
         connection = pyodbc.connect(connection_string)
         cursor = connection.cursor()
         query = "SELECT EvakuertID, ImageURL, Fornavn FROM Evakuerte WHERE ImageURL IS NOT NULL"
         cursor.execute(query)
         rows = cursor.fetchall()
        
         for row in rows:
             evakuert_id, image_url, fornavn = row
             try:
                 logger.debug(f"Fetching image for EvakuertID: {evakuert_id}, ImageURL: {image_url}")
                 response = requests.get(image_url)
                 if response.status_code == 200:
                     image_data = face.load_image_file(BytesIO(response.content))
                     encodings = face.face_encodings(image_data)
                     if len(encodings) > 0:
                         known_face_encodings.append(encodings[0])
                         known_face_ids.append(evakuert_id)
                         known_face_names.append(fornavn)
                     else:
                         logger.warning(f"No face found in image for EvakuertID: {evakuert_id}")
                 else:
                     logger.error(f"Failed to download image for EvakuertID {evakuert_id}: HTTP {response.status_code}")
             except Exception as e:
                 logger.error(f"Error processing image for EvakuertID {evakuert_id}: {e}")
        
         cursor.close()
         connection.close()
     except Exception as e:
         logger.error(f"Database error: {e}")
    
     return known_face_encodings, known_face_ids, known_face_names


def find_best_match(face_encoding, known_face_encodings, known_face_ids, known_face_names):
   
     if not known_face_encodings:
         logger.debug("No known faces available for matching.")
         return None, None, None
    
     face_distances = face.face_distance(known_face_encodings, face_encoding)
     best_match_index = np.argmin(face_distances)
     best_distance = face_distances[best_match_index]
    
     # Set your matching threshold – adjust if necessary
     threshold = 0.6
     logger.debug(f"Best match distance: {best_distance} (threshold: {threshold})")
   
     if best_distance <= threshold:
         logger.debug(f"Match found: EvakuertID={known_face_ids[best_match_index]}, Name={known_face_names[best_match_index]}")
         return known_face_ids[best_match_index], known_face_names[best_match_index], best_distance
     return None, None, None

@app.route('/register', methods=['GET', 'POST'])
def register():
    if "evakuert_id" not in session:
        return redirect(url_for("startID"))

    if request.method == 'POST':
        evakuert_id = session["evakuert_id"]
        result = get_evakuert_id_by_chipid(evakuert_id)
        return jsonify(result)

    return render_template('RFIDregister.html', evakuert_id=session["evakuert_id"])

@app.route('/api/scan', methods=['GET'])
def api_scan():
    if "evakuert_id" not in session:
        return jsonify({'error': 'No EvakuertID found in session'})

    scan_result = scan_rfid()

    if isinstance(scan_result, str):
        uid = scan_result
        evakuert_id = session["evakuert_id"]

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE RFID SET ChipID = ? WHERE EvakuertID = ?", (uid, evakuert_id))
            conn.commit()
            conn.close()

        return jsonify({
            'message': f'RFID {uid} linked to EvakuertID {evakuert_id}',
            'uid': uid
        })

    return jsonify(scan_result)

@app.route('/api/register_new_rfid', methods=['POST'])
def register_new_rfid():
    """Registers a new RFID card (ChipID) to the provided EvakuertID."""
    data = request.json
    evakuert_id = data.get("evakuert_id")
    chip_id = data.get("chip_id")

    if not evakuert_id or not chip_id:
        return jsonify({"error": "Missing Evakuert ID or RFID ChipID"}), 400

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()

        cursor.execute("SELECT EvakuertID FROM Evakuerte WHERE EvakuertID = ?", (evakuert_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Invalid Evakuert ID"}), 400

        cursor.execute("INSERT INTO RFID (ChipID, EvakuertID) VALUES (?, ?)", (chip_id, evakuert_id))
        conn.commit()
        conn.close()

        return jsonify({"message": f"RFID {chip_id} successfully linked to EvakuertID {evakuert_id}"}), 200

    return jsonify({"error": "Database connection failed"}), 500

@app.route('/start_register', methods=['POST'])
def start_register():
    try:
        f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

        while not f.readImage():
            pass

        f.convertImage(0x01)
        result = f.searchTemplate()
        positionNumber = result[0]

        if positionNumber == 0:
            return jsonify({"status": "Fingerprint already exists at position " + str(positionNumber)})

        return jsonify({"status": "Place the same finger again"}), 202

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Confirm Fingerprint Registration
@app.route('/confirm_register', methods=['POST'])
def confirm_register():
    try:
        f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

        timeout = time.time() + 10
        while not f.readImage():
            if time.time() > timeout:
                raise Exception("Timed out waiting for finger")

        f.convertImage(0x02)

        if f.compareCharacteristics() == 0:
            return jsonify({"error": "Fingers do not match"}), 400

        f.createTemplate()
        positionNumber = f.storeTemplate()

        return jsonify({"status": "Fingerprint registered", "evakuert_id": positionNumber})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Start Fingerprint Verification
@app.route('/start_verify', methods=['POST'])
def start_verify():
    try:
        f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

        if not f.verifyPassword():
            raise Exception("Sensor password invalid")

        timeout = time.time() + 10
        while not f.readImage():
            if time.time() > timeout:
                raise Exception("Timed out waiting for finger")

        f.convertImage(0x01)
        result = f.searchTemplate()
        positionNumber = result[0]
        accuracy = result[1]

        if positionNumber == -1:
            return jsonify({"status": "No match found"}), 404

        session['evakuert_id'] = positionNumber
        return jsonify({
            "status": "Match found",
            "evakuert_id": positionNumber,
            "accuracy": accuracy
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Capture Fingerprint Image
@app.route('/capture_fingerprint_image')
def capture_fingerprint_image():
    try:
        sensor = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

        if not sensor.verifyPassword():
            raise Exception('Incorrect sensor password')

        timeout = time.time() + 1
        while not sensor.readImage():
            if time.time() > timeout:
                return jsonify({'error': 'Timed out waiting for finger'}), 408

        base_dir = "fingerprints"
        os.makedirs(base_dir, exist_ok=True)

        evakuert_id = session.get("evakuert_id")
        if evakuert_id:
            filename = f"fingerprint_{evakuert_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        else:
            filename = f"fingerprint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        bmp_path = os.path.join(base_dir, f"{filename}.bmp")
        png_path = os.path.join(base_dir, f"{filename}.png")

        sensor.downloadImage(bmp_path)

        img = Image.open(bmp_path)
        img.save(png_path)

        return jsonify({
            "status": "Image captured",
            "url": f"/finger_image/{filename}.png"
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/recognize_fingerprint')
def recognize_fingerprint():
    try:
        
        sensor = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
        if not sensor.verifyPassword():
            raise Exception('Incorrect sensor password')
        
        timeout = time.time() + 10
        while not sensor.readImage():
            if time.time() > timeout:
                return jsonify({'error': 'Timed out waiting for finger'}), 408

        base_dir = "fingerprints"
        os.makedirs(base_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        generic_filename = f"scan_{timestamp}"
        bmp_path = os.path.join(base_dir, f"{generic_filename}.bmp")
        png_path = os.path.join(base_dir, f"{generic_filename}.png")

        sensor.downloadImage(bmp_path)
        Image.open(bmp_path).save(png_path)

        # 4. Use ORB to match against stored images
        orb = cv2.ORB_create()
        live_img = cv2.imread(png_path, 0)
        kp1, des1 = orb.detectAndCompute(live_img, None)

        best_match = None
        best_score = float('inf')
        matched_id = None

        for file in os.listdir(base_dir):
            if file.endswith(".png") and "fingerprint_" in file:
                template_path = os.path.join(base_dir, file)
                template_img = cv2.imread(template_path, 0)
                kp2, des2 = orb.detectAndCompute(template_img, None)

                if des1 is not None and des2 is not None:
                    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
                    matches = bf.match(des1, des2)
                    matches = sorted(matches, key=lambda x: x.distance)

                    score = sum([m.distance for m in matches[:10]])  # Lower = better
                    if score < best_score:
                        best_score = score
                        best_match = file
                        # Extract evakuert_id from filename: fingerprint_<id>_timestamp.png
                        try:
                            matched_id = file.split("_")[1]
                        except:
                            matched_id = None

        if best_match and matched_id:
            # 🔎 Fetch user's name from the database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Fornavn, MellomNavn, Etternavn FROM Evakuerte WHERE EvakuertID = ?", (matched_id,))
            user_row = cursor.fetchone()
            conn.close()

            if user_row:
                fornavn, mellomnavn, etternavn = user_row
                fullt_navn = f"{fornavn} {mellomnavn + ' ' if mellomnavn else ''}{etternavn}"
            else:
                fullt_navn = "Ukjent navn"

            session['evakuert_id'] = matched_id  # Store ID in session
            return jsonify({
                "status": "Match found",
                "evakuert_id": matched_id,
                "navn": fullt_navn,
                "matched_file": best_match
            })
        
    except Exception as e:
        print("[ERROR]", e)
        return jsonify({'error': str(e)}), 500
    
@app.route('/finger_image/<filename>')
def serve_fingerprint_image(filename):
    file_path = os.path.join("fingerprints", filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='image/png')
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)


