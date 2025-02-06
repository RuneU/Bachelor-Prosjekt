import os
import sys
sys.dont_write_bytecode = True
from flask import Flask, Response, render_template, request, redirect, url_for
import cv2

# Legg til 'sql' mappen i sys.path for å finne db_connection.py
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql'))

try:
    from db_connection import fetch_status_data, run_query, get_last_inserted_id  # Importer databasefunksjonen
except ImportError as e:
    print("Feil ved import av db_connection:", e)
    fetch_status_data = lambda: []  # Returner tom liste hvis import feiler

app = Flask(__name__)

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

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

@app.route("/admin")
def admin():
    statuses = fetch_status_data()  # Hent data fra databasen
    print("Statuses hentet fra DB:", statuses)  # Debug print
    return render_template("admin.html", statuses=statuses)


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
