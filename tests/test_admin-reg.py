import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from flask import Flask, template_rendered
from jinja2 import DictLoader
from contextlib import contextmanager

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the blueprint to test
from blueprints.admin_reg.routes import admin_reg_bp

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
        # Add a dummy index route
        @self.app.route('/')
        def index():
            return "Index Page"
        # Override the app's Jinja loader with a dummy template for testing
        self.app.jinja_loader = DictLoader({
        'admin-reg.html': 'Evakuert: {{ evakuert }}'
    })

        # Register the blueprint
        self.app.register_blueprint(admin_reg_bp)
        self.client = self.app.test_client()

    def test_handle_form_insert_success(self):
        """
        Test that a POST to /handle_form correctly performs an insert.
        The mock connection simulates returning IDs for the new records.
        """
        # For insertion, evakuert_id is empty (or non-digit)
        form_data = {
            'evakuert_id': '',
            'krise_id': '',
            'kontakt_person_id': '',
            'status_id': '',
            'status': 'Active',
            'krise-type': 'Emergency',
            'krise-navn': 'Test Crisis',
            'lokasjon': 'Test Location',
            'annen-info': 'Detailed Info',
            'evak-fnavn': 'John',
            'evak-mnavn': '',
            'evak-enavn': 'Doe',
            'evak-tlf': '1234567890',
            'evak-adresse': '123 Test St',
            'kon-fnavn': 'Jane',
            'kon-mnavn': '',
            'kon-enavn': 'Doe',
            'kon-tlf': '0987654321',
            'kon-adresse': '456 Other St'
        }

        # Set up a mock cursor and connection:
        mock_cursor = MagicMock()
        # Simulate fetchval: first call returns KriseID, second returns EvakuertID.
        mock_cursor.fetchval.side_effect = [1, 2]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        # Patch the connection function in our blueprint module.
        with patch('blueprints.admin_reg.routes.connection_def', return_value=mock_conn):
            response = self.client.post('/handle_form', data=form_data, follow_redirects=False)
            # Our route redirects on success.
            self.assertEqual(response.status_code, 302)
            # Ensure the transaction was committed.
            self.assertTrue(mock_conn.commit.called)
            # For an insert, the code should execute 4 queries.
            self.assertEqual(mock_cursor.execute.call_count, 4)

    def test_handle_form_update_success(self):
        """
        Test that a POST to /handle_form performs update queries when evakuert_id is provided.
        """
        # For updating, evakuert_id is a valid digit.
        form_data = {
            'evakuert_id': '2',
            'krise_id': '1',
            'kontakt_person_id': '3',
            'status_id': '4',
            'status': 'Inactive',
            'krise-type': 'Accident',
            'krise-navn': 'Updated Crisis',
            'lokasjon': 'New Location',
            'annen-info': 'Updated Info',
            'evak-fnavn': 'Alice',
            'evak-mnavn': '',
            'evak-enavn': 'Smith',
            'evak-tlf': '5551234567',
            'evak-adresse': '789 Test Ave',
            'kon-fnavn': 'Bob',
            'kon-mnavn': '',
            'kon-enavn': 'Johnson',
            'kon-tlf': '5557654321',
            'kon-adresse': '101 Test Blvd'
        }

        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        with patch('blueprints.admin_reg.routes.connection_def', return_value=mock_conn):
            response = self.client.post('/handle_form', data=form_data, follow_redirects=False)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(mock_conn.commit.called)
            # For update, the code executes 4 update queries.
            self.assertEqual(mock_cursor.execute.call_count, 4)

    def test_handle_form_missing_required_fields(self):
        """
        Test that if required fields (lokasjon and status) are missing, a 400 error is returned.
        """
        form_data = {
            'lokasjon': '',
            'status': ''
        }
        response = self.client.post('/handle_form', data=form_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Lokasjon and Status are required fields", response.data)

    def test_adminreg_with_id_found(self):
        """
        Test the GET /<int:evakuert_id> route returns a rendered template with expected data.
        """
        # Prepare a sample row as returned by the SELECT query.
        sample_row = [
            2,    # EvakuertID
            1,    # KriseID
            3,    # KontaktPersonID
            4,    # StatusID
            "John", "A", "Doe", "1234567890", "123 Test St",
            "Jane", "B", "Doe", "0987654321",
            "Emergency", "Test Crisis", "Test Location", "Detailed Info", "Active"
        ]
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = sample_row
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        with patch('blueprints.admin_reg.routes.connection_def', return_value=mock_conn):
            # Capture rendered templates to verify which template is used.
            with captured_templates(self.app) as templates:
                response = self.client.get('/2')
                # The response should be successful
                self.assertEqual(response.status_code, 200)
                # Verify the rendered template is the expected one.
                self.assertTrue(any("admin-reg.html" in t.name for t, ctx in templates))
                # Check that some expected content is in the output.
                self.assertIn(b"John", response.data)
                self.assertIn(b"Emergency", response.data)

    def test_adminreg_with_id_not_found(self):
        """
        Test that a GET request with a non-existent evakuert_id returns a 404.
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # Simulate no data found.
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        with patch('blueprints.admin_reg.routes.connection_def', return_value=mock_conn):
            response = self.client.get('/999')
            self.assertEqual(response.status_code, 404)
            self.assertIn(b"Evakuert not found", response.data)

if __name__ == '__main__':
    unittest.main()
