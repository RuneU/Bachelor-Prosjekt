import folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable, GeocoderRateLimited
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from blueprints.auth.auth import login_required
from sql.db_connection import (
    fetch_krise_by_id, update_krise, count_evakuerte_by_krise, fetch_status_counts_for_krise,
    count_evakuerte_same_location, count_evakuerte_different_location, fetch_krise_opprettet,
    fetch_combined_evakuerte_status_by_krise
)
from translations import translations
import time
from functools import lru_cache
import threading

admin_inc_bp = Blueprint('admin_inc', __name__, template_folder='../templates')

# Create a lock to prevent concurrent geocoding requests
geocode_lock = threading.Lock()

# Create a geolocator with increased timeout
geolocator = Nominatim(user_agent="my_flask_app", timeout=10)

# Cache for geocoding results to reduce API calls
@lru_cache(maxsize=128)
def geocode_location(location_str):
    """Cache geocoding results to reduce API calls to Nominatim"""
    try:
        # Use a lock to ensure only one request is sent at a time
        with geocode_lock:
            # Add delay to respect Nominatim's usage policy (1 request per second)
            time.sleep(1)
            return geolocator.geocode(location_str)
    except (GeocoderUnavailable, GeocoderRateLimited) as e:
        print(f"Geocoding error for {location_str}: {str(e)}")
        # Handle the rate limit error gracefully
        return None

# Cache for reverse geocoding results
@lru_cache(maxsize=128)
def reverse_geocode_coords(lat, lon):
    """Cache reverse geocoding results to reduce API calls to Nominatim"""
    try:
        # Use a lock to ensure only one request is sent at a time
        with geocode_lock:
            # Add delay to respect Nominatim's usage policy
            time.sleep(1)
            return geolocator.reverse((lat, lon))
    except (GeocoderUnavailable, GeocoderRateLimited) as e:
        print(f"Reverse geocoding error for {lat}, {lon}: {str(e)}")
        # Handle the rate limit error gracefully
        return None

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
        
        try:
            # Attempt to parse location_data as coordinates.
            coords = [float(coord.strip()) for coord in location_data.split(',')]
            # We'll use our cached function for reverse geocoding
            location_result = reverse_geocode_coords(coords[0], coords[1])
            if location_result:
                print("Address:", location_result.address)
            else:
                print("No address found for the given coordinates.")
            map_location = coords
        except ValueError:
            # If parsing fails, treat location_data as an address using cached function
            location_result = geocode_location(location_data)
            if location_result:
                coords = (location_result.latitude, location_result.longitude)
                print("Coordinates:", coords)
                map_location = [location_result.latitude, location_result.longitude]
            else:
                print(f"No coordinates found for the address: {location_data}")
                # Fallback coordinates - use a default location instead of trying to geocode
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
                # Skip geocoding if we've hit rate limits
                # Try to geocode only if we haven't hit too many requests
                if "Universitetet" in evac_location:  # Pre-defined coordinates for known locations
                    evac_coords = [60.3943055, 5.3259192]  # Example coordinates for university
                else:
                    # We'll attempt to geocode but be prepared to handle failure
                    evac_result = geocode_location(evac_location)
                    if evac_result:
                        evac_coords = [evac_result.latitude, evac_result.longitude]
                    else:
                        # If geocoding fails, use fallback coordinates and log
                        print(f"Geocoding failed for: {evac_location}. Using fallback coordinates.")
                        evac_coords = [0, 0]  # Fallback coordinates
            
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