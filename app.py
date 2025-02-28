import os
import sys
sys.dont_write_bytecode = True
from flask import Flask, request, render_template, jsonify, redirect, url_for, session
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql'))
from sql.db_connection import fetch_status_data, update_status, search_statuses, create_krise
from blueprints.admin_reg import admin_reg_bp
from blueprints.registrer.routes import registrer_bp
from blueprints.admin_inc.routes import admin_inc_bp
from dotenv import load_dotenv
from translations import translations

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key'

@app.route("/")
def index():
    lang = request.args.get('lang', session.get('lang', 'no'))
    session['lang'] = lang
    return render_template('index.html', t=translations.get(lang, translations['no']), lang=lang)

@app.route('/set_user_id', methods=['POST'])
def set_user_id():
    data = request.json
    if "evakuert_id" not in data or not data["evakuert_id"].isdigit():
        return jsonify({"error": "Invalid Evakuert ID"}), 400
    
    session["evakuert_id"] = int(data["evakuert_id"])
    return jsonify({"message": "User ID stored successfully"}), 200

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

# POST krise oppretelse til db
@app.route('/handle_incident', methods=['POST'])
def handle_incident():
    try:
        status = request.form.get('krise-status')
        krise_situasjon_type = request.form.get('krise-type') 
        krise_navn = request.form.get('krise-navn')
        lokasjon = request.form.get('krise-lokasjon')
        tekstboks = request.form.get('annen-info')

        if not all([status, krise_situasjon_type, krise_navn, lokasjon]):
            print('Vennligst fyll ut alle obligatoriske felt', 'error')
            return redirect(url_for('incident_creation'))

        if create_krise(status, krise_situasjon_type, krise_navn, lokasjon, tekstboks):
            print('Krise opprettet vellykket!', 'success')
        else:
            print('Feil ved opprettelse av krise', 'error')
            
        return redirect(url_for('index'))

    except Exception as e:
        print(f"Error: {str(e)}")
        print('En uventet feil oppsto', 'error')
        return redirect(url_for('incident_creation'))

@app.route('/incident_creation', methods=['GET', 'POST'])
def incident_creation():
    if request.method == 'POST':
        # Handle post if needed
        pass
    return render_template('incident_creation.html')

app.register_blueprint(admin_inc_bp)

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



