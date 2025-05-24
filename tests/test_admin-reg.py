import sys
import os
import unittest
from blueprints.admin_status.routes import admin_status_bp
from unittest.mock import MagicMock, patch
from flask import Flask, template_rendered, session # Import session
from jinja2 import DictLoader
from contextlib import contextmanager
import datetime # Added for mocking datetime objects if needed

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the blueprint to test
from blueprints.admin_reg.routes import admin_reg_bp
# Import the auth blueprint if its routes/decorators are hit indirectly
from blueprints.auth.auth import auth_bp, login_required

# Helper to capture rendered templates (optional, but useful to verify which template was used)
@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

class AdminRegIntegrationTest(unittest.TestCase):

    def setUp(self):
        # Create a Flask app for testing
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        # Set a secret key for session management (required for flash messages)
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        # Configure server name for url_for when testing redirects outside application context
        self.app.config['SERVER_NAME'] = 'localhost.test'

        # Override the app's Jinja loader with a dummy template for testing
        # Adjusted to use keys that will be in the context (e.g., evakuert.evak_fnavn)
        self.app.jinja_loader = DictLoader({
            'admin-reg.html': 'Evakuert: {{ evakuert.evak_fnavn if evakuert else "" }} Krise: {{ evakuert.krise_type if evakuert else ""}}',
            'login.html': 'Login Page' # Add dummy login template if redirects happen
        })

        # Register the blueprints. Ensure auth_bp is registered if its routes/decorators are involved
        # Correctly register admin_reg_bp with its URL prefix
        self.app.register_blueprint(admin_reg_bp, url_prefix='/admin-reg')
        self.app.register_blueprint(auth_bp, url_prefix='/auth') # Add url_prefix if needed
        self.app.register_blueprint(admin_status_bp, url_prefix='/admin-status')

        self.client = self.app.test_client()

    def test_handle_form_update_success(self):
        """
        Test that a POST to /admin-reg/handle_form performs update queries when evakuert_id is provided.
        """
        form_data = {
            'evakuert_id': '2', 'krise_id': '1', 'kontakt_person_id': '3', 
            # status_id is not directly used by the form processing for update in handle_form,
            # 'status' and 'evak-lokasjon' are used for the Status table update.
            'status': 'Inactive', # Route uses request.form.get('status')
            'evak-lokasjon': 'New Evacuee Location', # Route uses request.form.get('evak-lokasjon') for validation and Status table
            # Fields for Evakuerte table
            'evak-fnavn': 'Alice', 'evak-mnavn': '', 'evak-enavn': 'Smith', 'evak-tlf': '5551234567', 'evak-adresse': '789 Test Ave',
            # Fields for KontaktPerson table
            'kon-fnavn': 'Bob', 'kon-mnavn': '', 'kon-enavn': 'Johnson', 'kon-tlf': '5557654321',
            # These krise fields are in the form but not used by the update SQL in the route for an existing evakuert_id
            'krise-type': 'Accident', 'krise-navn': 'Updated Crisis', 'krise-lokasjon': 'Crisis Location Bravo', 
            'annen-info': 'Updated Info'
        }
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        with patch('blueprints.admin_reg.routes.connection_def', return_value=mock_conn):
            with self.client.session_transaction() as sess:
                sess['user_id'] = 1
            response = self.client.post('/admin-reg/handle_form', data=form_data, follow_redirects=False)
            if response.status_code == 400:
                print("Update test failed with 400. Response data:", response.data.decode())
            self.assertEqual(response.status_code, 302)
            self.assertTrue(mock_conn.commit.called)

    def test_handle_form_missing_required_fields(self):
        """
        Test that if required fields ('evak-lokasjon' and 'status') are missing, a 400 error is returned.
        """
        # Route expects 'evak-lokasjon' and 'status' from request.form
        form_data = {'evak-lokasjon': '', 'status': ''} 
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
        response = self.client.post('/admin-reg/handle_form', data=form_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"'evakuert lokasjon' and 'status' are required fields", response.data)

    def test_adminreg_with_id_found(self):
        """
        Test the GET /admin-reg/<int:evakuert_id> route returns a rendered template with expected data.
        """
        # This list must match the order and number of columns in the main SELECT query in adminreg_with_id route
        sample_row_tuple = (
            2,                                # e.EvakuertID
            1,                                # e.KriseID
            3,                                # kp.KontaktPersonID
            4,                                # s.StatusID
            "John",                           # e.Fornavn
            "A",                              # e.MellomNavn
            "Doe",                            # e.Etternavn
            "1234567890",                     # e.Telefonnummer
            "123 Test St",                    # e.Adresse
            "Jane",                           # kp.Fornavn (kon_fornavn)
            "B",                              # kp.MellomNavn (kon_mellomnavn)
            "DoeKontakt",                     # kp.Etternavn (kon_etternavn)
            "0987654321",                     # kp.Telefonnummer (kon_tlf)
            "EmergencyType",                  # kr.KriseSituasjonType
            "Test Crisis Name",               # kr.KriseNavn
            "Crisis Location Gamma",          # kr.Lokasjon (Krise lokasjon)
            "Some Detailed Info",             # kr.Tekstboks (AnnenInfo)
            "KriseStatusActive",              # kr.Status (krise_status)
            "EvacStatusCurrent",              # s.Status (evak_status)
            "EvacLocationDelta"               # s.Lokasjon (evak_lokasjon from Status table)
        )

        mock_logs_data = [
            ("Old Location Alpha", datetime.datetime(2023, 1, 1, 10, 0, 0)),
            ("Old Location Beta", datetime.datetime(2023, 1, 2, 11, 0, 0))
        ]
        mock_kriser_data = [
            (1, "Krise Alpha"),
            (5, "Krise Epsilon")
        ]

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = sample_row_tuple
        # fetchall is called twice: once for logs, once for kriser
        mock_cursor.fetchall.side_effect = [mock_logs_data, mock_kriser_data]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        with patch('blueprints.admin_reg.routes.connection_def', return_value=mock_conn):
            with captured_templates(self.app) as templates:
                with self.client.session_transaction() as sess:
                    sess['user_id'] = 1
                response = self.client.get('/admin-reg/2')
                self.assertEqual(response.status_code, 200)
                self.assertTrue(any("admin-reg.html" in t[0].name for t in templates))
                # Check based on the dummy template in setUp and evakuert_data keys
                self.assertIn(b"John", response.data) 
                self.assertIn(b"EmergencyType", response.data)
                # Check that logs and kriser were fetched
                self.assertEqual(mock_cursor.fetchall.call_count, 2)


    def test_adminreg_with_id_not_found(self):
        """
        Test that a GET request with a non-existent evakuert_id returns a 404.
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None # Simulate no record found
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        with patch('blueprints.admin_reg.routes.connection_def', return_value=mock_conn):
            with self.client.session_transaction() as sess:
                sess['user_id'] = 1
            response = self.client.get('/admin-reg/999') # Non-existent ID
            self.assertEqual(response.status_code, 404)
            self.assertIn(b"Evakuert not found", response.data)

if __name__ == '__main__':
    unittest.main()