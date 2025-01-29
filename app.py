import os
import sys
from flask import Flask, render_template

# Legg til 'sql' mappen i sys.path for å finne db_connection.py
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql'))

try:
    from db_connection import fetch_status_data  # Importer databasefunksjonen
except ImportError as e:
    print("Feil ved import av db_connection:", e)
    fetch_status_data = lambda: []  # Returner tom liste hvis import feiler

app = Flask(__name__)

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/admin")
def admin():
    try:
        statuses = fetch_status_data()  # Hent data fra databasen
        print("Statuses hentet fra DB:", statuses)  # Debug print
    except Exception as e:
        print("Feil ved henting av statusdata:", e)
        statuses = []  # Hvis en feil oppstår, send tom liste

    return render_template("admin.html", statuses=statuses)

if __name__ == '__main__':
    app.run(debug=True)
