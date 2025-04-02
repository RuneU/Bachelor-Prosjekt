import os
import sys
sys.dont_write_bytecode = True
from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, session
from sql.db_connection import connection_def
sys.path.append(os.path.join(os.path.dirname(__file__), 'sql'))
from sql.db_connection import fetch_all_kriser, search_krise, create_krise
from blueprints.admin_reg import admin_reg_bp
from blueprints.registrer.routes import registrer_bp
from blueprints.admin_inc.routes import admin_inc_bp
from blueprints.auth.auth import auth_bp, google_bp
from blueprints.admin_status.routes import admin_status_bp
from blueprints.evacuee_update.routes import evacuee_update_bp
from blueprints.incident_creation.routes import incident_creation_bp
from dotenv import load_dotenv
from translations import translations
from blueprints.auth.auth import login_required

load_dotenv()

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

# Register the blueprints
app.register_blueprint(admin_status_bp)
app.register_blueprint(admin_reg_bp, url_prefix='/admin-reg')
app.register_blueprint(registrer_bp)
app.register_blueprint(admin_inc_bp)
app.register_blueprint(auth_bp) 
app.register_blueprint(google_bp, url_prefix="/login")
app.register_blueprint(evacuee_update_bp)
app.register_blueprint(incident_creation_bp)

@app.route('/admin_page')
@login_required
def admin_page():
    lang = request.args.get('lang', session.get('lang', 'no'))
    session['lang'] = lang
    return render_template('admin_page.html', t=translations.get(lang, translations['no']), lang=lang)

@app.route('/admin_status_inc')
@login_required
def admin_status_inc():
    query = request.args.get('query', '')
    # Combined filter parameter: default is "nyeste"
    filter_order = request.args.get('filter_order', 'nyeste')
    
    # Determine status filter and ordering based on the selection
    if filter_order in ['nyeste', 'eldste']:
        status_filter = None
        order_by = 'new' if filter_order == 'nyeste' else 'old'
    elif filter_order == 'nykrise':
        status_filter = 'Ny krise'
        order_by = 'new'
    elif filter_order == 'paaagende':
        status_filter = 'Pågående'
        order_by = 'new'
    elif filter_order == 'ferdig':
        status_filter = 'Ferdig'
        order_by = 'new'
    else:
        status_filter = None
        order_by = 'new'
    
    # If a search query or status filter is provided, use search_krise; otherwise, fetch all
    if query or status_filter:
        krise_list = search_krise(query, status_filter, order_by)
    else:
        krise_list = fetch_all_kriser(order_by)
    
    lang = request.args.get('lang', session.get('lang', 'no'))
    session['lang'] = lang
    return render_template(
        'admin_status_inc.html', 
        krise_list=krise_list, 
        query=query, 
        filter_order=filter_order, t=translations.get(lang, translations['no']), lang=lang
    )

@app.route("/evacuee-search", methods=["GET", "POST"])
def evacuee_search():
    if request.method == "POST":
        evakuert_id = request.form.get("evakuertID")

        if not evakuert_id.isdigit():
            flash("Vennligst skriv inn en gyldig evakuertID.", "error")
            return redirect(url_for("evacuee_search"))

        evakuert_id = int(evakuert_id)

        conn = connection_def()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Evakuerte WHERE EvakuertID = ?", (evakuert_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result[0] > 0:
            return redirect(url_for("evacuee_update", evakuertID=evakuert_id))
        else:
            flash("Denne evakuertID finnes ikke.", "error")

            return redirect(url_for("evacuee_search"))
    lang = request.args.get('lang', session.get('lang', 'no'))
    session['lang'] = lang
    return render_template("evacuee_search.html", t=translations.get(lang, translations['no']), lang=lang)

@app.route("/evacuee-update/<int:evakuertID>")
def evacuee_update(evakuertID):
    return f"Oppdateringsside for evakuertID {evakuertID}"

@app.route("/newuser")
def newuser():
    return render_template("newuser.html")



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
