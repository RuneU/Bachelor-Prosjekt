from flask import Blueprint, render_template, request, redirect, url_for
import pyodbc
from sql.db_connection import connection_string, run_query, fetch_all_kriser, fetch_all_locations

registrer_bp = Blueprint('registrer', __name__)

@registrer_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            fornavn = request.form.get("fornavn")
            mellomnavn = request.form.get("mellomnavn")
            etternavn = request.form.get("etternavn")
            adresse = request.form.get("adresse")
            telefonnummer = request.form.get("telefonnummer")
            status = request.form.get("status")
            lokasjon_id = request.form.get("lokasjon")
            parorende_fornavn = request.form.get("parorende_fornavn")
            parorende_mellomnavn = request.form.get("parorende_mellomnavn")
            parorende_etternavn = request.form.get("parorende_etternavn")
            parorende_telefonnummer = request.form.get("parorende_telefonnummer")

            # Insert into Evakuerte and retrieve the new ID in one statement
            # Establish a connection and create a cursor
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()

            # Insert into Evakuerte and retrieve the new ID in one statement
            evakuert_query = """
            SET NOCOUNT ON;
            INSERT INTO Evakuerte (Fornavn, MellomNavn, Etternavn, Adresse, Telefonnummer)
            VALUES (?, ?, ?, ?, ?);
            SELECT SCOPE_IDENTITY() AS ID;
            """
            cursor.execute(evakuert_query, (fornavn, mellomnavn, etternavn, adresse, telefonnummer))
            row = cursor.fetchone()
            if row and row[0]:
                evakuert_id = int(row[0])
            else:
                raise Exception("Failed to retrieve a valid EvakuertID.")
            conn.commit()

            cursor.close()
            conn.close()




            # Insert into KontaktPerson using the newly obtained evakuert_id
            query_kontakt = f"""
                INSERT INTO KontaktPerson (Fornavn, MellomNavn, Etternavn, Telefonnummer, EvakuertID)
                VALUES ('{parorende_fornavn}', '{parorende_mellomnavn}', '{parorende_etternavn}', '{parorende_telefonnummer}', {evakuert_id});
            """
            run_query(query_kontakt)

            print("Request form data:", request.form)
            print("status:", request.form.get("status"))
            print("lokasjon:", request.form.get("lokasjon"))
            print("evakuert_id:", evakuert_id)

            # Insert into Status table using a parameterized query with dynamic values
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()
            query_status = "INSERT INTO Status ([Status], Lokasjon, EvakuertID) VALUES (?, ?, ?)"
            cursor.execute(query_status, (status, lokasjon_id, evakuert_id))
            conn.commit()
            cursor.close()
            conn.close()



            return redirect(url_for("index"))
        except Exception as e:
            print(f"An error occurred: {e}")
            return "An error occurred while processing your request."

    kriser = fetch_all_kriser()
    locations = fetch_all_locations()
    return render_template('register.html', kriser=kriser, locations=locations)
