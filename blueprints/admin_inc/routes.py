import folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from blueprints.auth.auth import login_required
from sql.db_connection import (
    fetch_krise_by_id, update_krise, count_evakuerte_by_krise, fetch_status_counts_for_krise,
    count_evakuerte_same_location, count_evakuerte_different_location, fetch_krise_opprettet,
    fetch_combined_evakuerte_status_by_krise
)
from translations import translations


admin_inc_bp = Blueprint('admin_inc', __name__, template_folder='../templates')

@admin_inc_bp.route('/admin-inc/<int:krise_id>')
@login_required
def admin_inc_detail(krise_id):
    lang = request.args.get('lang', session.get('lang', 'no'))
    session['lang'] = lang
    """Show details for a specific KriseID along with status counters and a map."""
    krise = fetch_krise_by_id(krise_id)
    if krise:
        evakuert_count = count_evakuerte_by_krise(krise_id)
        status_counts = fetch_status_counts_for_krise(krise_id)
        krise_opprettet = fetch_krise_opprettet(krise_id)
        same_count = count_evakuerte_same_location(krise['KriseID'], krise['Lokasjon'])
        diff_count = count_evakuerte_different_location(krise['KriseID'], krise['Lokasjon'])
        opprettet = fetch_krise_opprettet(krise['KriseID'])
        # Process the "Lokasjon" field: if it's coordinates, reverse geocode; if it's an address, geocode.
        location_data = krise['Lokasjon']
        geolocator = Nominatim(user_agent="my_flask_app")
        try:
            # Attempt to parse location_data as coordinates.
            coords = [float(coord.strip()) for coord in location_data.split(',')]
            # Reverse geocode to get a human-readable address.
            location_result = geolocator.reverse(coords)
            if location_result:
                print("Address:", location_result.address)
            else:
                print("No address found for the given coordinates.")
            map_location = coords
        except ValueError:
            # If parsing fails, treat location_data as an address.
            location_result = geolocator.geocode(location_data)
            if location_result:
                coords = (location_result.latitude, location_result.longitude)
                print("Coordinates:", coords)
                map_location = [location_result.latitude, location_result.longitude]
            else:
                print("No coordinates found for the given address.")
                map_location = [0, 0]  # Fallback coordinates
            
        # Generate the folium map using the determined coordinates
        m = folium.Map(location=map_location, zoom_start=11)
        marker_cluster = MarkerCluster().add_to(m)
        
        # Add the primary marker to the cluster
        folium.Marker(
            location=map_location,
            tooltip="Click me!",
            popup=f"Lokasjon: {location_data}",
            icon=folium.Icon(color="red")
        ).add_to(marker_cluster)
        
        # Fetch evacuee status for the table using the newly added function
        evakuerte_statuses = fetch_combined_evakuerte_status_by_krise(krise_id)
        
        # Dictionary to track markers placed at the same exact location
        placed_markers = {}
        
        # Add green marker(s) for each evacuee location into the cluster
        for evac in evakuerte_statuses:
            evac_location = evac.get('Lokasjon')
            # Use FullName from the DB result instead of Navn.
            navn = evac.get('FullName', 'N/A')
            status = evac.get('Status', 'N/A')
            try:
                # Attempt to parse evac_location as coordinates
                evac_coords = [float(coord.strip()) for coord in evac_location.split(',')]
            except ValueError:
                # Treat evac_location as an address if parsing fails
                evac_result = geolocator.geocode(evac_location)
                if evac_result:
                    evac_coords = [evac_result.latitude, evac_result.longitude]
                else:
                    evac_coords = [0, 0]  # Fallback coordinates if geocoding fails
            
            # Use a tuple for the coordinate key (rounded to avoid floating point issues)
            key = (round(evac_coords[0], 6), round(evac_coords[1], 6))
            count = placed_markers.get(key, 0)
            if count > 0:
                # Apply a slight offset depending on how many markers are already here.
                offset = 0.00005 * count
                evac_coords[0] += offset
                evac_coords[1] += offset
            placed_markers[key] = count + 1
            
            folium.Marker(
                location=evac_coords,
                tooltip=f"Evakuert Lokasjon: {evac_location}",
                popup=f"Evakuerte Lokasjon: {evac_location}<br>Navn: {navn}<br>Status: {status}",
                icon=folium.Icon(color="green")
            ).add_to(marker_cluster)
            
        kart_map = m._repr_html_()  # Alternative method to get HTML

        return render_template('admin_inc.html', t=translations.get(lang, translations['no']), lang=lang,
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
        flash(f"Krise with ID {krise_id} not found", "error", t=translations.get(lang, translations['no']), lang=lang)

        return redirect(url_for('admin_inc.admin_inc_list', t=translations.get(lang, translations['no']), lang=lang))

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
    return redirect(url_for('admin_status_inc'))