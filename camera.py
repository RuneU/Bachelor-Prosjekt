from flask import Flask, Response, render_template
import cv2
import os
import requests
import pyodbc
import base64
from dotenv import load_dotenv
from datetime import datetime


# Import database functions from db_connection.py
try:
    from sql.db_connection import run_query
except ImportError as e:
    print("Error importing db_connection:", e)


load_dotenv()

# Azure Face API, can consider later to move it to a hidden file, but only if we have time
AZURE_FACE_API_KEY = os.getenv("6kijocjJrw1Htp2V7Uv2uXkxVmxEIKo4qBwEsEUEkbTBoZaS27zJJQQJ99BBAC5RqLJXJ3w3AAAKACOGiv2C")
AZURE_FACE_API_ENGPOINT = os.getenv("https://fjesid.cognitiveservices.azure.com/")


# Define the new folder where images will be stored
IMAGE_DIR = "static/faces"
os.makedirs(IMAGE_DIR, exist_ok=True) 

app = Flask(__name__)


# This will generate the frames for camera capture
def generate_frames():
    camera = cv2.VideoCapture(0)  
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Detects Face using Azure Face API
def detect_face(image_path):
    try:
        with open(image_path, "rb") as img_file:
            image_data = base64.b64encode(img_file.read()).decode("utf-8")

        headers = {
            "Ocp-Apim-Subscription-Key": AZURE_FACE_API_KEY,
            "Content-Type": "application/octet-stream",
        }
        params = {"returnFaceId": "true"}

        with open(image_path, "rb") as image:
            response = requests.post(
                f"{AZURE_FACE_API_ENDPOINT}/face/v1.0/detect",
                headers=headers,
                params=params,
                data=image
            )

        faces = response.json()
        if faces and "faceId" in faces[0]:
            return faces[0]["faceId"]
        else:
            return None
    except Exception as e:
        print("Error detecting face:", e)
        return None

# Saves Captured Face to System & Database
def save_face(user_id):
    camera = cv2.VideoCapture(0)
    success, frame = camera.read()
    camera.release()

    if not success:
        return {"error": "Failed to capture image"}

    filename = f"user_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
    filepath = os.path.join(IMAGE_DIR, filename)

    cv2.imwrite(filepath, frame)

    image_url = f"/{filepath}"  # This allows Flask to serve it as a static file

    try:
        query = f"""
            UPDATE Evakuerte 
            SET PhotoURL = '{image_url}' 
            WHERE EvakuertID = {user_id}
        """
        run_query(query)  # Save in database

        return {"message": "Face saved successfully", "image_url": image_url}
    except Exception as e:
        return {"error": str(e)}
    


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/faceID')
def faceID():
    return render_template('faceID.html')

if __name__ == '__main__':
    app.run(debug=True)

