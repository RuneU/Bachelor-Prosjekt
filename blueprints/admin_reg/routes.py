from flask import Blueprint, render_template, request, redirect, url_for
from sql.db_connection import connection_def

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
        # Get form data
        form_data = {
            'evakuert_id': request.form.get('evakuert_id'),
            'krise_id': request.form.get('krise_id'),
            'kontakt_person_id': request.form.get('kontakt_person_id'),
            'status_id': request.form.get('status_id'),
            'status': request.form.get('status'),
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
            'kon_tlf': request.form.get('kon-tlf'),
            # 'kon_adresse': request.form.get('kon-adresse')
        }

        # Validate required fields
        if not all([form_data['krise_lokasjon'], form_data['status']]):
            return "Lokasjon and Status are required fields", 400

        conn = connection_def()
        cursor = conn.cursor()

        # Helper function to safely convert to int
        def safe_int(value):
            return int(value) if value and value.isdigit() else None
        is_update = form_data['evakuert_id'] and form_data['evakuert_id'].isdigit()
        if is_update:
            # Update existing records
            evakuert_id = safe_int(form_data['evakuert_id'])
            krise_id = safe_int(form_data['krise_id'])
            kontakt_person_id = safe_int(form_data['kontakt_person_id'])
            status_id = safe_int(form_data['status_id'])
            # Update Krise table
            cursor.execute("""
                UPDATE Krise 
                SET KriseSituasjonType = ?, KriseNavn = ?, Lokasjon = ?, Tekstboks = ?, Status = ?
                WHERE KriseID = ?
            """, (
                form_data['krise_type'],
                form_data['krise_navn'],
                form_data['krise_lokasjon'],
                form_data['annen_info'],
                form_data['status'],
                krise_id
            ))
            # Update Evakuerte table
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
            # Update KontaktPerson table
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
            # Update Status table
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
            # Insert new records (original insert logic)
            # 1. Insert into Krise table
            cursor.execute("""
                INSERT INTO Krise (KriseSituasjonType, KriseNavn, Lokasjon, Tekstboks, Status)
                OUTPUT INSERTED.KriseID
                VALUES (?, ?, ?, ?, ?)
            """, (
                form_data['krise_type'],
                form_data['krise_navn'],
                form_data['krise_lokasjon'],
                form_data['annen_info'],
                form_data['status']
            ))
            krise_id = cursor.fetchval()
            # 2. Insert into Evakuerte table
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
            # 3. Insert into KontaktPerson table
            cursor.execute("""
                INSERT INTO KontaktPerson (Fornavn, MellomNavn, Etternavn, Telefonnummer, EvakuertID)
                VALUES (?, ?, ?, ?, ?)
            """, (
                form_data['kon_fnavn'],
                form_data['kon_mnavn'],
                form_data['kon_enavn'],
                safe_int(form_data['kon_tlf']),
                evakuert_id
            ))
            # 4. Insert into Status table
            cursor.execute("""
                INSERT INTO Status (Status, Lokasjon, EvakuertID)
                VALUES (?, ?, ?)
            """, (
                form_data['status'],
                form_data['evak_lokasjon'],
                evakuert_id
            ))
        conn.commit()
        return redirect(url_for('index'))

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
                kp.KontaktPersonID,  -- Changed alias from k to kp
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
                s.Status,
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
            
            "EvakuertID": data[0], "KriseID": data[1], "KontaktPersonID": data[2],
            "StatusID": data[3], "evak_fnavn": data[4], "evak_mnavn": data[5],
            "evak_enavn": data[6], "evak_tlf": data[7], "evak_adresse": data[8], 
            "kon_fnavn": data[9], "kon_mnavn": data[10], "kon_enavn": data[11], 
            "kon_tlf": data[12], "krise_type": data[13], "krise_navn": data[14], 
            "krise_lokasjon": data[15], "annen_info": data[16], "status": data[17],
            "evak_lokasjon": data[18]
        }

        return render_template("admin-reg.html", evakuert=evakuert_data)
    
    except Exception as e:
        return f"Database error: {e}", 500
    
    finally:
        cursor.close()
        conn.close()