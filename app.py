import os
import sys
import cv2
sys.dont_write_bytecode = True
from flask import Flask, Response, request, render_template, jsonify, redirect, send_from_directory, url_for
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql'))
from blueprints.admin_reg import admin_reg_bp
from blueprints.registrer.routes import registrer_bp

try:
    from camera import generate_frames, save_face
except ImportError as e:
    print("Feil ved import av camera.py:", e)

app = Flask(__name__)


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

app.register_blueprint(admin_reg_bp, url_prefix='/admin-reg')
app.register_blueprint(registrer_bp)

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

@app.route('/save_face', methods=['POST'])
def save_face_route():
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    result = save_face(user_id)
    return jsonify(result)

@app.route('/static/faces/<filename>')
def serve_face_image(filename):
    return send_from_directory("static/faces", filename)

@app.route('/faceID')
def faceID():
    return render_template('faceID.html')

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

if __name__ == '__main__':
    app.run(debug=True)
