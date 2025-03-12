import sys
from flask import jsonify
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sql.db_connection import connection_def
sys.dont_write_bytecode = True

admin_reg_bp = Blueprint('admin_reg', __name__, template_folder='../templates')

@admin_reg_bp.route('/')
def admin_reg():
    return render_template("admin-reg.html")

def safe_int(value):
    """Helper function to safely convert to integer"""
    return int(value) if value and value.isdigit() else None

@admin_reg_bp.route('/handle_form', methods=['POST'])
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
            'krise_status': request.form.get('krise-status'),
            'krise_type': request.form.get('krise-type'),
            'krise_navn': request.form.get('krise-navn'),
            'krise_lokasjon': request.form.get('krise-lokasjon'),
            'annen_info': request.form.get('annen-info'),
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

        if not all([form_data['krise_lokasjon'], form_data['status']]):
            return "Lokasjon and Status are required fields", 400

        conn = connection_def()
        cursor = conn.cursor()

        def safe_int(value):
            return int(value) if value and value.isdigit() else None

        is_update = form_data['evakuert_id'] and form_data['evakuert_id'].isdigit()
        if is_update:
            evakuert_id = safe_int(form_data['evakuert_id'])
            new_krise_id = safe_int(form_data['krise_id'])
            kontakt_person_id = safe_int(form_data['kontakt_person_id'])
            status_id = safe_int(form_data['status_id'])
            
            # Update only the Evakuerte table to point to the new KriseID.
            cursor.execute("""
                UPDATE Evakuerte 
                SET KriseID = ?
                WHERE EvakuertID = ?
            """, (new_krise_id, evakuert_id))
            
            # Continue updating the other tables as before.
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
            # Insert new records as before...
            cursor.execute("""
                INSERT INTO Krise (KriseSituasjonType, KriseNavn, Lokasjon, Tekstboks, Status)
                OUTPUT INSERTED.KriseID
                VALUES (?, ?, ?, ?, ?)
            """, (
                form_data['krise-type'],
                form_data['krise-navn'],
                form_data['krise-lokasjon'],
                form_data['annen-info'],
                form_data['krise-status'],
            ))
            krise_id = cursor.fetchval()
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
                safe_int(form_data['kon_tlf']),
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
        return redirect(url_for('admin_status.admin'))
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


@admin_reg_bp.route('/<int:evakuert_id>')
def adminreg_with_id(evakuert_id):
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
                kp.Etternavn AS kon_etternavn, 
                kp.Telefonnummer AS kon_tlf,
                kr.KriseSituasjonType, 
                kr.KriseNavn, 
                kr.Lokasjon, 
                kr.Tekstboks,
                kr.Status AS krise_status,
                s.Status AS evak_status,
                s.Lokasjon
            FROM Evakuerte e
            LEFT JOIN KontaktPerson kp ON e.EvakuertID = kp.EvakuertID
            LEFT JOIN Krise kr ON e.KriseID = kr.KriseID
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
            "krise_type": data[13],
            "krise_navn": data[14],
            "krise_lokasjon": data[15],
            "annen_info": data[16],
            "krise_status": data[17],
            "evak_status": data[18],
            "evak_lokasjon": data[19]
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

        return render_template("admin-reg.html", evakuert=evakuert_data, logs=logs, kriser=kriser)
    
    except Exception as e:
        return f"Database error: {e}", 500
    
    finally:
        cursor.close()
        conn.close()

from flask import jsonify

@admin_reg_bp.route('/get_krise_details/<int:krise_id>')
def get_krise_details(krise_id):
    conn = connection_def()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT KriseSituasjonType, KriseNavn, Lokasjon, Tekstboks, Status
            FROM Krise
            WHERE KriseID = ?
        """, (krise_id,))
        row = cursor.fetchone()
        if row:
            data = {
                "KriseSituasjonType": row[0],
                "KriseNavn": row[1],
                "Lokasjon": row[2],
                "Tekstboks": row[3],
                "Status": row[4]
            }
            return jsonify(data)
        else:
            return jsonify({"error": "Krise not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
