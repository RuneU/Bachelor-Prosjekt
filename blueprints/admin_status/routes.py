from flask import Blueprint, render_template, request, redirect, url_for
from sql.db_connection import fetch_status_data, fetch_all_kriser, update_status, search_statuses
from auth import login_required

admin_status_bp = Blueprint('admin_status', __name__)
@admin_status_bp.route("/admin")
@login_required
@admin_status_bp.route("/admin")
def admin():
    statuses = fetch_status_data()
    krise_options = fetch_all_kriser()
    print(krise_options)  # Debugging line to check the fetched data
    return render_template("admin_status.html", statuses=statuses, krise_options=krise_options)

@admin_status_bp.route('/update_status/<int:evakuert_id>', methods=['POST'])
def update_status_route(evakuert_id):
    status = request.form['status']
    lokasjon = request.form['lokasjon']
    update_status(evakuert_id, status, lokasjon)
    return redirect(url_for('admin_status.admin'))

@admin_status_bp.route("/search", methods=["GET"])
def search():
    query = request.args.get("query")
    krise_id = request.args.get("KriseID")
    statuses = search_statuses(query, krise_id)
    krise_options = fetch_all_kriser()
    return render_template("admin_status.html", statuses=statuses, krise_options=krise_options)