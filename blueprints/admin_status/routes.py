from flask import Blueprint, render_template, request, redirect, url_for, session
from sql.db_connection import fetch_status_data, fetch_all_kriser, update_status, search_statuses
from blueprints.auth.auth import login_required
from translations import translations
admin_status_bp = Blueprint('admin_status', __name__)


@admin_status_bp.route("/admin")
@login_required
def admin():
    statuses = fetch_status_data()
    krise_options = fetch_all_kriser()
    print(krise_options)  # Debugging line to check the fetched data

    lang = request.args.get('lang', session.get('lang', 'no'))
    session['lang'] = lang
    return render_template("admin_status.html", t=translations.get(lang, translations['no']), lang=lang, statuses=statuses, krise_options=krise_options)

@admin_status_bp.route('/update_status/<int:evakuert_id>', methods=['POST'])
@login_required
def update_status_route(evakuert_id):
    status = request.form['status']
    lokasjon = request.form['lokasjon']
    update_status(evakuert_id, status, lokasjon)
    lang = request.args.get('lang', session.get('lang', 'no'))
    session['lang'] = lang
    return redirect(url_for('admin_status.admin', t=translations.get(lang, translations['no']), lang=lang))


@admin_status_bp.route("/search", methods=["GET"])
@login_required
def search():
    query = request.args.get("query")
    krise_id = request.args.get("KriseID")
    statuses = search_statuses(query, krise_id)
    krise_options = fetch_all_kriser()
    
    lang = request.args.get('lang', session.get('lang', 'no'))
    session['lang'] = lang
    return render_template("admin_status.html", t=translations.get(lang, translations['no']), lang=lang, statuses=statuses, krise_options=krise_options)