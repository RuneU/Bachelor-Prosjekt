import os
import sys
import requests
from io import BytesIO
import cv2
import pyodbc
import numpy as np
import face_recognition as face
from face_utils import save_face
import mysql.connector
sys.dont_write_bytecode = True
from datetime import datetime
from flask import Flask, Response, request, render_template, jsonify, redirect, url_for, session, send_from_directory
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql'))
from sql.db_connection import fetch_status_data, update_status, search_statuses
from blueprints.admin_reg import admin_reg_bp
from dotenv import load_dotenv
import logging

# Configure logging
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

camera = cv2.VideoCapture(0)  # Open webcam

FACES_FOLDER = "static/faces"

load_dotenv()

# Database Connection (Loaded from `.env`)
DB_DRIVER = os.getenv("DB_DRIVER")
DB_SERVER = os.getenv("DB_SERVER")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_UID = os.getenv("DB_UID")
DB_PWD = os.getenv("DB_PWD")

AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
if AZURE_CONNECTION_STRING is None:
    raise ValueError("AZURE_STORAGE_CONNECTION_STRING is not set. Check your .env file!")

CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")


def get_db_connection():
    return mysql.connector.connect(AZURE_CONNECTION_STRING)

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")




@app.route('/set_user_id', methods=['POST'])
def set_user_id():
    data = request.json
    if "evakuert_id" not in data or not data["evakuert_id"].isdigit():
        return jsonify({"error": "Invalid Evakuert ID"}), 400
    
    session["evakuert_id"] = int(data["evakuert_id"])
    return jsonify({"message": "User ID stored successfully"}), 200



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            fornavn = request.form.get("fornavn")
            mellomnavn = request.form.get("mellomnavn")
            etternavn = request.form.get("etternavn")
            adresse = request.form.get("adresse")
            telefonnummer = request.form.get("telefonnummer")
            status = request.form.get("status")
            parorende_fornavn = request.form.get("parorende_fornavn")
            parorende_mellomnavn = request.form.get("parorende_mellomnavn")
            parorende_etternavn = request.form.get("parorende_etternavn")
            parorende_telefonnummer = request.form.get("parorende_telefonnummer")

            # Insert data into the database
            query = f"""
                INSERT INTO Evakuerte (Fornavn, MellomNavn, Etternavn, Adresse, Telefonnummer)
                VALUES ('{fornavn}', '{mellomnavn}', '{etternavn}', '{adresse}', '{telefonnummer}');
            """
            run_query(query)

            # Get the last inserted EvakuertID
            evakuert_id = get_last_inserted_id()

            # Insert data into the KontaktPerson table
            query = f"""
                INSERT INTO KontaktPerson (Fornavn, MellomNavn, Etternavn, Telefonnummer, EvakuertID)
                VALUES ('{parorende_fornavn}', '{parorende_mellomnavn}', '{parorende_etternavn}', '{parorende_telefonnummer}', {evakuert_id});
            """
            run_query(query)

            # Insert data into the Status table
            query = f"""
                INSERT INTO Status (Status, Lokasjon, EvakuertID)
                VALUES ('{status}', '{adresse}', {evakuert_id});
            """
            run_query(query)

            return redirect(url_for("index"))
        except Exception as e:
            print(f"An error occurred: {e}")
            return "An error occurred while processing your request."

    return render_template("register.html")

    


# Hent data fra databasen og route til Admin page
@app.route("/admin")
def admin():
        statuses = fetch_status_data()  
        return render_template("admin.html", statuses=statuses)

# Status for evakuerte på admin page
@app.route('/update_status/<int:evakuert_id>', methods=['POST'])
def update_status_route(evakuert_id):
    status = request.form['status']
    lokasjon = request.form['lokasjon']
    update_status(evakuert_id, status, lokasjon)
    return redirect(url_for('admin'))

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query")
    krise_id = request.args.get("KriseID")
    if query or krise_id:
        statuses = search_statuses(query, krise_id)
    else:
        statuses = fetch_status_data()
    
    return render_template("admin.html", statuses=statuses)

app.register_blueprint(admin_reg_bp, url_prefix='/admin-reg')
app.register_blueprint(registrer_bp)


@app.route('/capture')
def capture_page():
    return render_template('capture.html')


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
        # Get the first detected face (assuming only one face is present)
        (x, y, w, h) = faces[0]

        # Crop the image to focus on the detected face
        image_cropped = image[y:y+h, x:x+w]
        return image_cropped

    # If no face is detected, return the original image
    return image


@app.route("/iot")
def iot():
    return render_template("iot.html")

@app.route("/startID")
def startID():
    return render_template("startID.html")

@app.route("/newuser")
def newuser():
    return render_template("newuser.html")

@app.route("/iot_login")
def iot_login():
    return render_template("iot_login.html")









"""
    Koden under her skal jeg få inn i egen fil, men akkurat nå vil jeg få det til å funke(azure blob container vil ikke åpne bilde)
    """










@app.route('/capture_face', methods=['POST'])
def capture_face():
    global latest_frame
    if latest_frame is None:
        logger.error("No frame available. Is the camera running?")
        return jsonify({"success": False, "message": "No frame available."})
    
    # Create a unique filename for the captured face image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = f"static/captured_face_{timestamp}.jpg"
    
    try:
        cv2.imwrite(image_path, latest_frame)
        logger.debug(f"Face captured and saved as '{image_path}'")
    except Exception as e:
        logger.error(f"Failed to save image: {e}")
        return jsonify({"success": False, "message": "Failed to save image."})
    
    # Match the captured face against known faces from the database
    recognized_faces = recognize_faces_from_image(image_path)
    
    if recognized_faces:
        return jsonify({"success": True, "recognized_faces": recognized_faces})
    else:
        return jsonify({"success": False, "message": "No faces recognized."})

def recognize_faces_from_image(image_path):
    # Gather known faces from the Evakuerte table
    known_face_encodings, known_face_ids, known_face_names = fetch_known_faces_from_db()
    
    # Load and encode the captured face image
    image = face.load_image_file(image_path)
    captured_encodings = face.face_encodings(image)
    
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
    
    connection_string = f"DRIVER={DB_DRIVER};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_UID};PWD={DB_PWD}"
    
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
    
    if best_distance < threshold:
        logger.debug(f"Match found: EvakuertID={known_face_ids[best_match_index]}, Name={known_face_names[best_match_index]}")
        return known_face_ids[best_match_index], known_face_names[best_match_index], best_distance
    return None, None, None

def generate_frames_with_progress():
    
    global latest_frame
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        logger.error("Failed to open camera.")
        return
    
    try:
        while True:
            success, frame = camera.read()
            if not success:
                logger.error("Failed to read frame from camera.")
                break
            
            # Update the global latest_frame for capture_face to use
            latest_frame = frame.copy()
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        camera.release()


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

# Route for the recognition page
@app.route('/recognition')
def recognition():
    return render_template('recognition.html')



if __name__ == '__main__':
    app.run(debug=True)



