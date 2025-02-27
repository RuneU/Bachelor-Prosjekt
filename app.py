import os
import sys
sys.dont_write_bytecode = True
from flask import Flask, request, render_template, jsonify, redirect, url_for, session
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql'))
from sql.db_connection import connection_string, fetch_status_data, update_status, search_statuses
from blueprints.admin_reg import admin_reg_bp
from dotenv import load_dotenv
from translations import translations


load_dotenv()

from blueprints.registrer.routes import registrer_bp


app = Flask(__name__)
app.secret_key = 'your-secret-key'


@app.route("/")
def index():
    lang = request.args.get('lang', session.get('lang', 'no'))
    session['lang'] = lang
    return render_template('index.html', t=translations.get(lang, translations['no']), lang=lang)


@app.route('/set_user_id', methods=['POST'])
def set_user_id():
    data = request.json
    if "evakuert_id" not in data or not data["evakuert_id"].isdigit():
        return jsonify({"error": "Invalid Evakuert ID"}), 400
    
    session["evakuert_id"] = int(data["evakuert_id"])
    return jsonify({"message": "User ID stored successfully"}), 200


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

    


# Hent data fra databasen og route til Admin page
@app.route("/admin")
def admin():
        statuses = fetch_status_data()  
        return render_template("admin.html", statuses=statuses)

# Status for evakuerte på admin page
@app.route('/update_status/<int:evakuert_id>', methods=['POST'])
def update_status_route(evakuert_id):
    status = request.form['status']
    lokasjon = request.form['lokasjon']
    update_status(evakuert_id, status, lokasjon)
    return redirect(url_for('admin'))

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query")
    krise_id = request.args.get("KriseID")
    if query or krise_id:
        statuses = search_statuses(query, krise_id)
    else:
        statuses = fetch_status_data()
    
    return render_template("admin.html", statuses=statuses)

app.register_blueprint(admin_reg_bp, url_prefix='/admin-reg')
app.register_blueprint(registrer_bp)


if __name__ == '__main__':
    app.run(debug=True)



