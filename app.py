import os
import sys
sys.dont_write_bytecode = True
from flask import Flask, Response, request, render_template, jsonify
import cv2

# Legg til 'sql' mappen i sys.path for å finne db_connection.py
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql'))

try:
    from db_connection import fetch_status_data  # Importer databasefunksjonen
except ImportError as e:
    print("Feil ved import av db_connection:", e)
    fetch_status_data = lambda: []  # Returner tom liste hvis import feiler

try:
    from camera import generate_frames, save_face
except ImportError as e:
    print("Feil ved import av camera.py:", e)

app = Flask(__name__)

# 🎥 **Video Feed Route**
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# 📷 **Save Face Route**
@app.route('/save_face', methods=['POST'])
def save_face_route():
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    result = save_face(user_id)
    return jsonify(result)

# ✅ Route to Serve Saved Images
@app.route('/static/faces/<filename>')
def serve_face_image(filename):
    return send_from_directory("static/faces", filename)

@app.route('/faceID')
def faceID():
    return render_template('faceID.html')


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")


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

@app.route("/admin")
def admin():
        statuses = fetch_status_data()  # Hent data fra databasen
        print("Statuses hentet fra DB:", statuses)  # Debug print
        return render_template("admin.html", statuses=statuses)

if __name__ == '__main__':
    app.run(debug=True)
