from flask import Blueprint, render_template, request, redirect, url_for
from sql.db_connection import fetch_all_kriser, fetch_all_locations, run_query, get_last_inserted_id

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
            krise_id = request.form.get("krise-navn")
            parorende_fornavn = request.form.get("parorende_fornavn")
            parorende_mellomnavn = request.form.get("parorende_mellomnavn")
            parorende_etternavn = request.form.get("parorende_etternavn")
            parorende_telefonnummer = request.form.get("parorende_telefonnummer")

            # Fetch LokasjonID based on LokasjonNavn
            query = f"SELECT LokasjonID FROM Lokasjon WHERE LokasjonNavn = '{lokasjon_id}'"
            lokasjon_result = run_query(query)
            if not lokasjon_result:
                raise ValueError(f"Lokasjon '{lokasjon_id}' not found.")
            lokasjon_id = lokasjon_result[0]['LokasjonID']

            # Fetch KriseID based on KriseNavn
            query = f"SELECT KriseID FROM Krise WHERE KriseNavn = '{krise_id}'"
            krise_result = run_query(query)
            if not krise_result:
                raise ValueError(f"Krise '{krise_id}' not found.")
            krise_id = krise_result[0]['KriseID']

            # Insert data into the Evakuerte table
            query = f"""
                INSERT INTO Evakuerte (Fornavn, MellomNavn, Etternavn, Adresse, Telefonnummer, KriseID)
                VALUES ('{fornavn}', '{mellomnavn}', '{etternavn}', '{adresse}', '{telefonnummer}', {krise_id});
            """
            run_query(query)

            # Get the last inserted EvakuertID
            evakuert_id = get_last_inserted_id()
            if not evakuert_id:
                raise ValueError("Failed to retrieve last inserted EvakuertID.")

            # Insert data into the KontaktPerson table
            query = f"""
                INSERT INTO KontaktPerson (Fornavn, MellomNavn, Etternavn, Telefonnummer, EvakuertID)
                VALUES ('{parorende_fornavn}', '{parorende_mellomnavn}', '{parorende_etternavn}', '{parorende_telefonnummer}', {evakuert_id});
            """
            run_query(query)

            # Insert data into the Status table
            query = f"""
                INSERT INTO Status (Status, Lokasjon, EvakuertID)
                VALUES ('{status}', '{lokasjon_id}', {evakuert_id});
            """
            run_query(query)

            return redirect(url_for("index"))
        except Exception as e:
            print(f"An error occurred: {e}")
            return f"An error occurred while processing your request: {e}"

    kriser = fetch_all_kriser()  # Fetch all kriser from the database
    locations = fetch_all_locations()  # Fetch all locations from the database
    return render_template('register.html', kriser=kriser, locations=locations)

