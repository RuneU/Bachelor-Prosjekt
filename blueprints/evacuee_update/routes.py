import sys
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from sql.db_connection import connection_def
sys.dont_write_bytecode = True
evacuee_update_bp = Blueprint('evacuee_update', __name__, template_folder='../templates')
from translations import translations
def safe_int(value):
    """Helper function to safely convert to integer"""
    return int(value) if value and value.isdigit() else None

@evacuee_update_bp.route('/handle_form', methods=['POST'])
def handle_form():
    conn = None
    cursor = None
    try:
        form_data = {
            'evakuert_id': request.form.get('evakuert_id'),
            'krise_id': request.form.get('krise_id'), 
            'kontakt_person_id': request.form.get('kontakt_person_id'),
            'status_id': request.form.get('status_id'),
            'status': request.form.get('status'),
            'evak_fnavn': request.form.get('evak-fnavn'),
            'evak_mnavn': request.form.get('evak-mnavn'),
            'evak_enavn': request.form.get('evak-enavn'),
            'evak_tlf': request.form.get('evak-tlf'),
            'evak_adresse': request.form.get('evak-adresse'),
            'evak_lokasjon': request.form.get('evak-lokasjon'),
            'kon_fnavn': request.form.get('kon-fnavn'),
            'kon_mnavn': request.form.get('kon-mnavn'),
            'kon_enavn': request.form.get('kon-enavn'),
            'kon_tlf': request.form.get('kon-tlf')
        }

        # Validate required fields
        if not form_data['status']:
            return "Status is a required field", 400

        conn = connection_def()
        cursor = conn.cursor()

        def safe_int(value):
            return int(value) if value and value.isdigit() else None

        is_update = form_data['evakuert_id'] and form_data['evakuert_id'].isdigit()
        if is_update:
            evakuert_id = safe_int(form_data['evakuert_id'])
            kontakt_person_id = safe_int(form_data['kontakt_person_id'])
            status_id = safe_int(form_data['status_id'])
            
            # Do not update KriseID; update only the fields in Evakuerte.
            cursor.execute("""
                UPDATE Evakuerte 
                SET Fornavn = ?, MellomNavn = ?, Etternavn = ?, 
                    Telefonnummer = ?, Adresse = ?
                WHERE EvakuertID = ?
            """, (
                form_data['evak_fnavn'],
                form_data['evak_mnavn'],
                form_data['evak_enavn'],
                safe_int(form_data['evak_tlf']),
                form_data['evak_adresse'],
                evakuert_id
            ))
            cursor.execute("""
                UPDATE KontaktPerson 
                SET Fornavn = ?, MellomNavn = ?, Etternavn = ?, Telefonnummer = ?
                WHERE KontaktPersonID = ?
            """, (
                form_data['kon_fnavn'],
                form_data['kon_mnavn'],
                form_data['kon_enavn'],
                safe_int(form_data['kon_tlf']),
                kontakt_person_id
            ))
            cursor.execute("""
                UPDATE Status 
                SET Status = ?, Lokasjon = ?
                WHERE StatusID = ?
            """, (
                form_data['status'],
                form_data['evak_lokasjon'],
                status_id
            ))
        else:
            # Do not insert into Krise; set KriseID to None.
            krise_id = None
            cursor.execute("""
                INSERT INTO Evakuerte (Fornavn, MellomNavn, Etternavn, Telefonnummer, Adresse, KriseID)
                OUTPUT INSERTED.EvakuertID
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                form_data['evak_fnavn'],
                form_data['evak_mnavn'],
                form_data['evak_enavn'],
                safe_int(form_data['evak_tlf']),
                form_data['evak_adresse'],
                krise_id
            ))
            evakuert_id = cursor.fetchval()
            cursor.execute("""
                INSERT INTO KontaktPerson (Fornavn, MellomNavn, Etternavn, Telefonnummer, EvakuertID)
                VALUES (?, ?, ?, ?, ?)
            """, (
                form_data['kon_fnavn'],
                form_data['kon_mnavn'],
                form_data['kon-enavn'],
                safe_int(form_data['kon-tlf']),
                evakuert_id
            ))
            cursor.execute("""
                INSERT INTO Status (Status, Lokasjon, EvakuertID)
                VALUES (?, ?, ?)
            """, (
                form_data['status'],
                form_data['evak_lokasjon'],
                evakuert_id
            ))
        conn.commit()
        
        lang = request.args.get('lang', session.get('lang', 'no'))
        session['lang'] = lang
        return redirect(url_for('index', t=translations.get(lang, translations['no']), lang=lang))
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

@evacuee_update_bp.route('/evacuee-update/<int:evakuert_id>')
def adminreg_with_id(evakuert_id):
    lang = request.args.get('lang', session.get('lang', 'no'))
    session['lang'] = lang
    t = translations.get(lang, translations['no'])

    conn = connection_def()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                e.EvakuertID, 
                e.KriseID, 
                kp.KontaktPersonID, 
                s.StatusID,
                e.Fornavn, 
                e.MellomNavn, 
                e.Etternavn, 
                e.Telefonnummer, 
                e.Adresse,
                kp.Fornavn AS kon_fornavn, 
                kp.MellomNavn AS kon_mellomnavn, 
                kp.Etternavn AS kon_enavn, 
                kp.Telefonnummer AS kon_tlf,
                s.Status AS evak_status,
                s.Lokasjon
            FROM Evakuerte e
            LEFT JOIN KontaktPerson kp ON e.EvakuertID = kp.EvakuertID
            LEFT JOIN Status s ON e.EvakuertID = s.EvakuertID
            WHERE e.EvakuertID = ?
        """, (evakuert_id,))
        
        data = cursor.fetchone()
        
        if not data:
            return "Evakuert not found", 404

        evakuert_data = {
            "EvakuertID": data[0],
            "KriseID": data[1],
            "KontaktPersonID": data[2],
            "StatusID": data[3],
            "evak_fnavn": data[4],
            "evak_mnavn": data[5],
            "evak_enavn": data[6],
            "evak_tlf": data[7],
            "evak_adresse": data[8], 
            "kon_fnavn": data[9],
            "kon_mnavn": data[10],
            "kon_enavn": data[11],
            "kon_tlf": data[12],
            "evak_status": data[13],
            "evak_lokasjon": data[14]
        }

        # Fetch log data for this EvakuertID.
        cursor.execute("""
            SELECT old_lokasjon, change_date
            FROM Lokasjon_log
            WHERE evakuert_id = ?
            ORDER BY change_date DESC
        """, (evakuert_id,))
        logs = [dict(old_lokasjon=row[0], change_date=row[1]) for row in cursor.fetchall()]

        # Also fetch all crisis records for the dropdown.
        cursor.execute("SELECT KriseID, KriseNavn FROM Krise")
        kriser = cursor.fetchall()


        return render_template("evacuee_update.html", t=t, lang=lang, evakuert=evakuert_data, logs=logs, kriser=kriser)
    
    except Exception as e:
        return f"Database error: {e}", 500
    
    finally:
        cursor.close()
        conn.close()
