import os
import sys
sys.dont_write_bytecode = True
# Legg til 'sql' mappen i sys.path for å finne db_connection.py
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql'))
from db_connection import fetch_status_data  # No try-except needed here
import cv2
from flask import Flask, render_template, request, redirect, url_for
from sql.db_connection import fetch_status_data, update_status

app = Flask(__name__)

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/admin")
def admin():
        statuses = fetch_status_data()  # Hent data fra databasen
        return render_template("admin.html", statuses=statuses)

@app.route('/update_status/<int:evakuert_id>', methods=['POST'])
def update_status_route(evakuert_id):
    status = request.form['status']
    lokasjon = request.form['lokasjon']
    update_status(evakuert_id, status, lokasjon)
    return redirect(url_for('admin'))


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

@app.route("/iot")
def iot():
    return render_template("iot.html")

@app.route("/startID")
def startID():
    return render_template("startID.html")

if __name__ == '__main__':
    app.run(debug=True)
