from flask import Blueprint, render_template, request, redirect, url_for, session
from sql.db_connection import create_krise
from blueprints.auth.auth import login_required
from translations import translations
incident_creation_bp = Blueprint('incident_creation', __name__)

# POST krise oppretelse til db
@incident_creation_bp.route('/handle_incident', methods=['POST'])
@login_required
def handle_incident():
    lang = request.args.get('lang', session.get('lang', 'no'))
    session['lang'] = lang
    try:
        status = request.form.get('krise-status')
        krise_situasjon_type = request.form.get('krise-type') 
        krise_navn = request.form.get('krise-navn')
        lokasjon = request.form.get('krise-lokasjon')
        tekstboks = request.form.get('annen-info')

        if not all([status, krise_situasjon_type, krise_navn, lokasjon]):
            print('Vennligst fyll ut alle obligatoriske felt', 'error')
            return redirect(url_for('incident_creation.incident_creation'))

        if create_krise(status, krise_situasjon_type, krise_navn, lokasjon, tekstboks):
            print('Krise opprettet vellykket!', 'success')
        else:
            print('Feil ved opprettelse av krise', 'error')
        return redirect(url_for('index', t=translations.get(lang, translations['no']), lang=lang))
    
    except Exception as e:
        print(f"Error: {str(e)}")
        print('En uventet feil oppsto', 'error')
        return redirect(url_for('incident_creation.incident_creation', t=translations.get(lang, translations['no']), lang=lang))


@incident_creation_bp.route('/incident_creation', methods=['GET', 'POST'])
@login_required
def incident_creation():
    lang = request.args.get('lang', session.get('lang', 'no'))
    session['lang'] = lang
    t = translations.get(lang, translations['no'])
    return render_template('incident_creation.html', t=t, lang=lang)
