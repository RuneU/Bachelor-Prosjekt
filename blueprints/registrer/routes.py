import sys
from flask import jsonify
from flask import Blueprint, render_template, request, redirect, url_for
from sql.db_connection import connection_def
sys.dont_write_bytecode = True

registrer_bp = Blueprint('registrer', __name__)

@registrer_bp.route("/register", methods=["GET", "POST"])
def register():
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