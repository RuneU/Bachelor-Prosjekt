from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
import pyodbc
from sql.db_connection import connection_string, fetch_all_locations, fetch_all_krise_situasjon_types
from translations import translations

registrer_bp = Blueprint('registrer', __name__)

@registrer_bp.route("/register", methods=["GET", "POST"])
def register():
    try:
        if request.method == "POST":
            # Get form data
            evak_fnavn = request.form.get("evak-fnavn")
            evak_mnavn = request.form.get("evak-mnavn")
            evak_enavn = request.form.get("evak-enavn")
            evak_adresse = request.form.get("evak-adresse")
            evak_tlf = request.form.get("evak-tlf")
            status = request.form.get("status")
            evak_lokasjon = request.form.get("evak-lokasjon")
            krise_id = request.form.get("krise_id")
            kon_fnavn = request.form.get("kon-fnavn")
            kon_mnavn = request.form.get("kon-mnavn")
            kon_enavn = request.form.get("kon-enavn")
            kon_tlf = request.form.get("kon-tlf")

            print(f"Received KriseID: {krise_id}")  # Debugging

            if not krise_id or not krise_id.isdigit():
                return "Error: Invalid KriseID received", 400  

            krise_id = int(krise_id)

            # Verify KriseID exists in the Krise table
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Krise WHERE KriseID = ?", (krise_id,))
            row = cursor.fetchone()
            if row[0] == 0:
                return "Error: KriseID does not exist in the database", 400

            print("Inserting into Evakuerte...")  # Debugging

            # Insert into Evakuerte and fetch the inserted ID using OUTPUT INSERTED
            evakuert_query = """
            INSERT INTO Evakuerte (Fornavn, MellomNavn, Etternavn, Adresse, Telefonnummer, KriseID)
            OUTPUT INSERTED.EvakuertID
            VALUES (?, ?, ?, ?, ?, ?);
            """
            cursor.execute(evakuert_query, (evak_fnavn, evak_mnavn, evak_enavn, evak_adresse, evak_tlf, krise_id))
            row = cursor.fetchone()

            print(f"Retrieved EvakuertID: {row}")  # Debugging
            if row and row[0]:
                evakuert_id = int(row[0])
            else:
                return "Error: Failed to retrieve a valid EvakuertID", 500

            print(f"EvakuertID to be used in KontaktPerson: {evakuert_id}")

            # Insert into KontaktPerson
            query_kontakt = """
                INSERT INTO KontaktPerson (Fornavn, MellomNavn, Etternavn, Telefonnummer, EvakuertID)
                VALUES (?, ?, ?, ?, ?);
            """
            cursor.execute(query_kontakt, (kon_fnavn, kon_mnavn, kon_enavn, kon_tlf, evakuert_id))
            conn.commit()
            print("Pårørende successfully inserted!")

            # Insert into Status table
            query_status = "INSERT INTO Status ([Status], Lokasjon, EvakuertID) VALUES (?, ?, ?)"
            cursor.execute(query_status, (status, evak_lokasjon, evakuert_id))
            conn.commit()

            cursor.close()
            conn.close()

            # Redirect user to the temporary page showing their evakuertID
            return redirect(url_for("registrer.show_evakuert", evakuert_id=evakuert_id))

    except Exception as e:
        print(f"An error occurred: {e}")
        return f"<h2>An error occurred:</h2> <p>{e}</p>", 500 

    # Fetch all crisis details (for auto-populate support)
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("SELECT KriseID, KriseNavn, KriseSituasjonType, Lokasjon, Status FROM Krise")
    kriser = cursor.fetchall()  # This returns tuples (assuming your DB driver does so)

    cursor.close()
    conn.close()
    lang = request.args.get('lang', session.get('lang', 'no'))
    session['lang'] = lang

    return render_template('register.html', t=translations.get(lang, translations['no']), lang=lang,
                           kriser=kriser, 
                           locations=fetch_all_locations(), 
                           krise_situasjon_types=fetch_all_krise_situasjon_types())


@registrer_bp.route("/register/show_evakuert/<int:evakuert_id>")
def show_evakuert(evakuert_id):
    lang = request.args.get('lang', session.get('lang', 'no'))
    session['lang'] = lang
    return render_template("show_evakuertID.html", t=translations.get(lang, translations['no']), lang=lang, evakuertID=evakuert_id)


@registrer_bp.route('/register/get_krise_details/<krise_id>')
def get_krise_details(krise_id):
    """Endpoint to fetch crisis details by KriseID."""
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        query = """
            SELECT KriseSituasjonType, KriseNavn, Lokasjon, Tekstboks, Status
            FROM Krise
            WHERE KriseID = ?
        """
        cursor.execute(query, (krise_id,))
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