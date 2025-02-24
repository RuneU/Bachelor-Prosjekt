import cv2
import os
import base64
from datetime import datetime
import pyodbc
import numpy as np
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from flask import Flask, Response, request, render_template, jsonify, redirect, url_for, session
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Load environment variables
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

blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# Load pre-trained face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


# Attempt to connect to Azure
try:
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    azure_available = True
except Exception as e:
    print(f"Azure connection failed: {e}")
    azure_available = False


import cv2


def load_known_faces(faces_folder):
    """Load known faces and their IDs from the specified folder."""
    known_face_encodings = []
    known_face_ids = []

    for filename in os.listdir(faces_folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            # Load the image
            image_path = os.path.join(faces_folder, filename)
            image = face_utils.load_image_file(image_path)

            # Encode the face
            face_encoding = face_utils.face_encodings(image)[0]

            # Extract the ID from the filename (e.g., "user1.jpg" -> "user1")
            face_id = os.path.splitext(filename)[0]

            # Add to the known faces list
            known_face_encodings.append(face_encoding)
            known_face_ids.append(face_id)

    return known_face_encodings, known_face_ids


# Function to insert face metadata into the database
def insert_face_metadata(evakuert_id, image_url):
    """Update the Evakuerte table with the ImageURL for the given EvakuertID."""
    connection_string = f"DRIVER={DB_DRIVER};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_UID};PWD={DB_PWD}"
    try:
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        # Update the ImageURL for the given EvakuertID
        query = "UPDATE Evakuerte SET ImageURL = ? WHERE EvakuertID = ?"
        cursor.execute(query, image_url, evakuert_id)

        connection.commit()
        cursor.close()
        connection.close()
        logger.info(f"Metadata updated for EvakuertID: {evakuert_id}")
    except Exception as e:
        logger.error(f"Failed to update face metadata: {e}")


def generate_frames(evakuert_id=None):  # Pass the ID explicitly
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    camera = cv2.VideoCapture(0)

    face_captured = False

    while True:
        success, frame = camera.read()
        if not success:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        height, width, _ = frame.shape
        center_x, center_y = width // 2, height // 2
        box_size = 200
        box_top_left = (center_x - box_size // 2, center_y - box_size // 2)
        box_bottom_right = (center_x + box_size // 2, center_y + box_size // 2)

        cv2.rectangle(frame, box_top_left, box_bottom_right, (255, 0, 0), 2)

        face_inside_box = False
        for (x, y, w, h) in faces:
            if (x > box_top_left[0] and y > box_top_left[1] and
                x + w < box_bottom_right[0] and y + h < box_bottom_right[1]):
                face_inside_box = True
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            else:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        if face_inside_box and not face_captured:
            cv2.imwrite("captured_face.jpg", frame)
            print(f"Face captured and saved as 'captured_face.jpg' for EvakuertID: {evakuert_id}")
            face_captured = True

        if not face_inside_box:
            face_captured = False


def save_face(evakuert_id, image_data):
    """Save a detected face to Azure and update the database."""
    try:
        evakuert_id = int(evakuert_id)
    except ValueError:
        return jsonify({"error": "Invalid Evakuert ID"}), 400

    # Remove base64 header
    image_data = image_data.split(",")[1] if "," in image_data else image_data

    if not evakuert_id:
        return jsonify({"error": "Evakuert ID is required"}), 400

    # Generate a unique filename using the current time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
    filename = f"evakuert_{evakuert_id}_{timestamp}.jpg"  # Unique filename

    try:
        img_bytes = base64.b64decode(image_data)

        # Upload to Azure Blob Storage
        blob_client = container_client.get_blob_client(filename)
        blob_client.upload_blob(img_bytes, overwrite=True)

        # Get the URL of the uploaded image
        image_url = blob_client.url

        # Update the Evakuerte table with the ImageURL
        insert_face_metadata(evakuert_id, image_url)  # Call the correct function

        logger.info(f"Photo saved to Azure: {filename}")
        return jsonify({"message": f"Photo saved to Azure: {filename}", "image_url": image_url}), 200

    except Exception as e:
        logger.error(f"Azure upload failed: {e}")

        # Fallback: Save locally
        os.makedirs("static/faces", exist_ok=True)
        local_path = os.path.join("static", "faces", filename)

        with open(local_path, "wb") as f:
            f.write(img_bytes)

        logger.info(f"Photo saved locally: {local_path}")
        return jsonify({"message": f"Photo saved locally: {local_path}"}), 200

def recognize_face():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    camera = cv2.VideoCapture(0)

    while True:
        success, frame = camera.read()
        if not success:
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            face = frame[y:y+h, x:x+w]
            face_filename = f"face_{x}_{y}.jpg"
            cv2.imwrite(face_filename, face)
            
            # Upload face to Azure Blob Storage
            blob_client = container_client.get_blob_client(face_filename)
            with open(face_filename, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            image_url = blob_client.url

            # Store face metadata in Azure Cosmos DB
            face_metadata = {
                "id": f"face_{x}_{y}",
                "image_url": image_url
            }
            container_db.upsert_item(face_metadata)

            os.remove(face_filename)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def upload_to_azure(filename):
    """Uploads a face image to Azure Blob Storage."""
    blob_client = container_client.get_blob_client(filename)
    with open(filename, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    print(f"Uploaded {filename} to Azure.")


def fetch_face_from_azure(filename):
    """Retrieves a face image from Azure Blob Storage."""
    blob_client = container_client.get_blob_client(filename)
    return blob_client.download_blob().readall()
