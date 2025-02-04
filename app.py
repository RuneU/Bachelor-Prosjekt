import os
import sys
from flask import Flask, Response, render_template, request, redirect, url_for
import cv2

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

@app.route("/admin-reg")
def adminreg():
    return render_template("admin-reg.html")

@app.route('/handle_form', methods=['POST'])
def handle_form():
    if request.method == 'POST':
        try:
            # Get form data
            form_data = {
                'status': request.form.get('status'),
                'krise-type': request.form.get('krise-type'),
                'krise-navn': request.form.get('krise-navn'),
                'lokasjon': request.form.get('lokasjon'),
                'annen-info': request.form.get('annen-info'),
                'evak-fnavn': request.form.get('evak-fnavn'),
                'evak-mnavn': request.form.get('evak-mnavn'),
                'evak-enavn': request.form.get('evak-enavn'),
                'evak-tlf': request.form.get('evak-tlf'),
                'evak-adresse': request.form.get('evak-adresse'),
                'kon-fnavn': request.form.get('kon-fnavn'),
                'kon-mnavn': request.form.get('kon-mnavn'),
                'kon-enavn': request.form.get('kon-enavn'),
                'kon-tlf': request.form.get('kon-tlf'),
                'kon-adresse': request.form.get('kon-adresse')
            }

            # Insert into database
            cursor = conn.cursor()
            sql = """INSERT INTO your_table_name 
                     (status, krise_type, krise_navn, lokasjon, annen_info, 
                      evak_fnavn, evak_mnavn, evak_enavn, evak_tlf, evak_adresse,
                      kon_fnavn, kon_mnavn, kon_enavn, kon_tlf, kon_adresse)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            
            cursor.execute(sql, tuple(form_data.values()))
            conn.commit()
            cursor.close()
            
            return redirect(url_for('success_page'))  # Redirect to a success page
            
        except Exception as e:
            conn.rollback()
            return f"An error occurred: {str(e)}"

@app.route('/success')
def success_page():
    return "Data successfully submitted!"



if __name__ == '__main__':
    app.run(debug=True)
