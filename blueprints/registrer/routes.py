from flask import Blueprint, render_template, request, redirect, url_for
import pyodbc
from sql.db_connection import connection_string, fetch_all_kriser, fetch_all_locations, fetch_all_krise_situasjon_types

registrer_bp = Blueprint('registrer', __name__)

@registrer_bp.route("/register", methods=["GET", "POST"])
def register():
    try:
        if request.method == "POST":
            # Get form data
            fornavn = request.form.get("fornavn")
            mellomnavn = request.form.get("mellomnavn")
            etternavn = request.form.get("etternavn")
            adresse = request.form.get("adresse")
            telefonnummer = request.form.get("telefonnummer")
            status = request.form.get("status")
            lokasjon = request.form.get("lokasjon")
            krise_id = request.form.get("krise_id")
            parorende_fornavn = request.form.get("parorende_fornavn")
            parorende_mellomnavn = request.form.get("parorende_mellomnavn")
            parorende_etternavn = request.form.get("parorende_etternavn")
            parorende_telefonnummer = request.form.get("parorende_telefonnummer")

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
            cursor.execute(evakuert_query, (fornavn, mellomnavn, etternavn, adresse, telefonnummer, krise_id))
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
            cursor.execute(query_kontakt, (parorende_fornavn, parorende_mellomnavn, parorende_etternavn, parorende_telefonnummer, evakuert_id))
            conn.commit()
            print("Pårørende successfully inserted!")

            # Insert into Status table
            query_status = "INSERT INTO Status ([Status], Lokasjon, EvakuertID) VALUES (?, ?, ?)"
            cursor.execute(query_status, (status, lokasjon, evakuert_id))
            conn.commit()

            cursor.close()
            conn.close()

            return redirect(url_for("index"))

    except Exception as e:
        print(f"An error occurred: {e}")
        return f"<h2>An error occurred:</h2> <p>{e}</p>", 500 

    # Fetch all crisis details (Auto-populate support)
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("SELECT KriseID, KriseNavn, KriseSituasjonType, Lokasjon FROM Krise")
    kriser = [
        {
            "KriseID": row[0],
            "KriseNavn": row[1],
            "KriseSituasjonType": row[2],
            "Lokasjon": row[3]
        }
        for row in cursor.fetchall()
    ]
    cursor.close()
    conn.close()

    return render_template('register.html', kriser=kriser, locations=fetch_all_locations(), krise_situasjon_types=fetch_all_krise_situasjon_types())
