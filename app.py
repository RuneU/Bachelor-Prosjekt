import os
import sys
from flask import Flask, Response, render_template, request, redirect, url_for
from blueprints.admin_reg import admin_reg_bp
import cv2

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sql.db_connection import connection_def


# Legg til 'sql' mappen i sys.path for å finne db_connection.py
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql'))

try:
    from db_connection import fetch_status_data  # Importer databasefunksjonen
except ImportError as e:
    print("Feil ved import av db_connection:", e)
    fetch_status_data = lambda: []  # Returner tom liste hvis import feiler

app = Flask(__name__)

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

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

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

@app.route("/admin")
def admin():
    try:
        statuses = fetch_status_data()  # Hent data fra databasen
        print("Statuses hentet fra DB:", statuses)  # Debug print
    except Exception as e:
        print("Feil ved henting av statusdata:", e)
        statuses = []  # Hvis en feil oppstår, send tom liste

    return render_template("admin.html", statuses=statuses)

app.register_blueprint(admin_reg_bp, url_prefix='/admin-reg')

@app.route("/admin-reg")
def adminreg():
    return render_template("admin-reg.html")

if __name__ == '__main__':
    app.run(debug=True)
