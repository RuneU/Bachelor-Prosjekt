import os
import sys
from flask import Flask, Response, render_template, request, redirect, url_for
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
                'krise_type': request.form.get('krise-type'),
                'krise_navn': request.form.get('krise-navn'),
                'lokasjon': request.form.get('lokasjon'),
                'annen_info': request.form.get('annen-info'),
                'evak_fnavn': request.form.get('evak-fnavn'),
                'evak_mnavn': request.form.get('evak-mnavn'),
                'evak_enavn': request.form.get('evak-enavn'),
                'evak_tlf': request.form.get('evak-tlf'),
                'evak_adresse': request.form.get('evak-adresse'),
                'kon_fnavn': request.form.get('kon-fnavn'),
                'kon_mnavn': request.form.get('kon-mnavn'),
                'kon_enavn': request.form.get('kon-enavn'),
                'kon_tlf': request.form.get('kon-tlf'),
                'kon_adresse': request.form.get('kon-adresse')
            }

            # Validate required fields
            if not all([form_data['lokasjon'], form_data['status']]):
                return "Lokasjon and Status are required fields", 400

            conn = connection_def()
            cursor = conn.cursor()

            # 1. Insert into Krise table
            cursor.execute("""
                INSERT INTO Krise (KriseSituasjonType, KriseNavn, Lokasjon, Tekstboks, Status)
                OUTPUT INSERTED.KriseID
                VALUES (?, ?, ?, ?, ?)
            """, (
                form_data['krise_type'],
                form_data['krise_navn'],
                form_data['lokasjon'],
                form_data['annen_info'],
                form_data['status']
            ))
            krise_id = cursor.fetchval()
            if not krise_id:
                raise ValueError("Failed to insert into Krise table")

            # 2. Insert into Evakuerte table
            cursor.execute("""
                INSERT INTO Evakuerte (Fornavn, MellomNavn, Etternavn, Telefonnummer, Adresse, KriseID)
                OUTPUT INSERTED.EvakuertID
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                form_data['evak_fnavn'],
                form_data['evak_mnavn'],
                form_data['evak_enavn'],
                int(form_data['evak_tlf']) if form_data['evak_tlf'] else None,
                form_data['evak_adresse'],
                krise_id
            ))
            evakuert_id = cursor.fetchval()
            if not evakuert_id:
                raise ValueError("Failed to insert into Evakuerte table")

            # 3. Insert into KontaktPerson table
            cursor.execute("""
                INSERT INTO KontaktPerson (Fornavn, MellomNavn, Etternavn, Telefonnummer, EvakuertID)
                VALUES (?, ?, ?, ?, ?)
            """, (
                form_data['kon_fnavn'],
                form_data['kon_mnavn'],
                form_data['kon_enavn'],
                int(form_data['kon_tlf']) if form_data['kon_tlf'] else None,
                evakuert_id
            ))

            # 4. Insert into Status table
            cursor.execute("""
                INSERT INTO Status (Status, Lokasjon, EvakuertID)
                VALUES (?, ?, ?)
            """, (
                form_data['status'],
                form_data['lokasjon'],
                evakuert_id
            ))

            conn.commit()
            return redirect(url_for('success_page'))

        except ValueError as ve:
            conn.rollback()
            return f"Invalid input format: {str(ve)}", 400
        except Exception as e:
            conn.rollback()
            return f"Database error: {str(e)}", 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

@app.route("/admin-reg/<int:evakuert_id>")
def adminreg_with_id(evakuert_id):
    conn = connection_def()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT e.Fornavn, e.MellomNavn, e.Etternavn, e.Telefonnummer, e.Adresse,
                k.Fornavn AS kon_fornavn, k.MellomNavn AS kon_mellomnavn, k.Etternavn AS kon_etternavn, k.Telefonnummer AS kon_tlf,
                kr.KriseSituasjonType, kr.KriseNavn, kr.Lokasjon, kr.Tekstboks, s.Status
            FROM Evakuerte e
            LEFT JOIN KontaktPerson k ON e.EvakuertID = k.EvakuertID
            LEFT JOIN Krise kr ON e.KriseID = kr.KriseID
            LEFT JOIN Status s ON e.EvakuertID = s.EvakuertID
            WHERE e.EvakuertID = ?
        """, (evakuert_id,))

        
        data = cursor.fetchone()
        
        if not data:
            return "Evakuert not found", 404

        evakuert_data = {
            "evak_fnavn": data[0], "evak_mnavn": data[1], "evak_enavn": data[2], 
            "evak_tlf": data[3], "evak_adresse": data[4], 
            "kon_fnavn": data[5], "kon_mnavn": data[6], "kon_enavn": data[7], 
            "kon_tlf": data[8], 
            "krise_type": data[9], "krise_navn": data[10], "lokasjon": data[11], 
            "annen_info": data[12], "status": data[13]
        }

        return render_template("admin-reg.html", evakuert=evakuert_data)
    
    except Exception as e:
        return f"Database error: {e}", 500
    
    finally:
        cursor.close()
        conn.close()


@app.route('/success')
def success_page():
    return "Data successfully submitted!"


if __name__ == '__main__':
    app.run(debug=True)
