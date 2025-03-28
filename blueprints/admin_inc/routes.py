import folium
from flask import Blueprint, render_template, request, redirect, url_for, flash
from blueprints.auth.auth import login_required
from sql.db_connection import (
    fetch_krise_by_id, update_krise, count_evakuerte_by_krise, fetch_status_counts_for_krise,
    count_evakuerte_same_location, count_evakuerte_different_location, fetch_krise_opprettet,
    fetch_combined_evakuerte_status_by_krise
)

admin_inc_bp = Blueprint('admin_inc', __name__, template_folder='../templates')

@admin_inc_bp.route('/admin-inc/<int:krise_id>')
@login_required
def admin_inc_detail(krise_id):
    """Show details for a specific KriseID along with status counters and a map."""
    krise = fetch_krise_by_id(krise_id)
    if krise:
        evakuert_count = count_evakuerte_by_krise(krise_id)
        status_counts = fetch_status_counts_for_krise(krise_id)
        krise_opprettet = fetch_krise_opprettet(krise_id)
        same_count = count_evakuerte_same_location(krise['KriseID'], krise['Lokasjon'])
        diff_count = count_evakuerte_different_location(krise['KriseID'], krise['Lokasjon'])
        opprettet = fetch_krise_opprettet(krise['KriseID'])
        # Convert the string location to a list of floats if necessary
        location_data = krise['Lokasjon']
        if isinstance(location_data, str):
            location_data = [float(coord.strip()) for coord in location_data.split(',')]
        # Generate the folium map using the parsed location data
        m = folium.Map(location=location_data, zoom_start=11)
        folium.Marker(
            location=location_data,
            tooltip="Click me!",
            popup=f"Lokasjon: {location_data}",
            icon=folium.Icon(color="red")
        ).add_to(m)
        kart_map = m._repr_html_()  # Alternative method to get HTML

        # New: Fetch evacuee status for the table using the newly added function
        evakuerte_statuses = fetch_combined_evakuerte_status_by_krise(krise_id)

        return render_template('admin_inc.html',
                               krise=krise,
                               evakuert_count=evakuert_count,
                               status_counts=status_counts,
                               krise_opprettet=krise_opprettet,
                               same_count=same_count,
                               diff_count=diff_count,
                               opprettet=opprettet,
                               kart_map=kart_map,
                               evakuerte_statuses=evakuerte_statuses)
    else:
        flash(f"Krise with ID {krise_id} not found", "error")
        return redirect(url_for('admin_inc.admin_inc_list'))

@admin_inc_bp.route('/update_krise/<int:krise_id>', methods=['POST'])
@login_required
def update_krise_route(krise_id):
    """Handle updates for a specific KriseID"""
    status = request.form.get('krise-status')
    krise_type = request.form.get('krise-type')
    krise_navn = request.form.get('krise-navn')
    lokasjon = request.form.get('krise-lokasjon')
    tekstboks = request.form.get('annen-info')

    if update_krise(krise_id, status, krise_type, krise_navn, lokasjon, tekstboks):
        flash('Incident updated successfully', 'success')
    else:
        flash('Error updating incident', 'error')

    # Redirect to the index page after update
    return redirect(url_for('index'))