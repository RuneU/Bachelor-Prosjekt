import unittest
from flask import Flask, url_for
from unittest.mock import patch, MagicMock
import pyodbc
from sql.db_connection import connection_string
# Assuming your Blueprint is named 'registrer_bp' and is in 'blueprints.registrer.routes'
from blueprints.registrer.routes import registrer_bp

class TestRegisterRoute(unittest.TestCase):

    def setUp(self):
        """Set up a new app instance for each test."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing forms
        self.app.config['SERVER_NAME'] = 'localhost.localdomain' # Necessary for url_for, .localdomain or other TLD often needed
        self.app.register_blueprint(registrer_bp, url_prefix='/registrer')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push() # Push an application context

    def tearDown(self):
        """Clean up after each test."""
        self.app_context.pop() # Pop the application context

    @patch('blueprints.registrer.routes.pyodbc.connect')
    def test_register_evacuee_success(self, mock_connect):
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock fetchone for KriseID check to return a count of 1 (krise exists)
        # and then the EvakuertID after insert
        mock_cursor.fetchone.side_effect = [
            (1,),  # For KriseID check
            (123,) # For OUTPUT INSERTED.EvakuertID
        ]
        # Mock fetchall for the GET request part of the route (loading kriser)
        # This might be called if the initial POST fails and it re-renders the template
        # or if other parts of the setup call it.
        mock_cursor.fetchall.return_value = []

        form_data = {
            "evak-fnavn": "Test",
            "evak-mnavn": "Middle",
            "evak-enavn": "User",
            "evak-adresse": "123 Test St",
            "evak-tlf": "12345678",
            "status": "Evakuert",
            "evak-lokasjon": "Evakueringssenter A",
            "krise_id": "1",
            "kon-fnavn": "Kontakt",
            "kon-mnavn": "",
            "kon-enavn": "Person",
            "kon-tlf": "87654321"
        }

        response = self.client.post(url_for('registrer.register'), data=form_data)

        # Assertions
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertEqual(response.headers['Location'], url_for('registrer.show_evakuert', evakuert_id=123, _external=False))

        # Verify database calls
        # The connection_string is imported directly now, so it will be used by the patched pyodbc.connect
        mock_connect.assert_called_once_with(connection_string)

        # Check KriseID validation call
        mock_cursor.execute.assert_any_call("SELECT COUNT(*) FROM Krise WHERE KriseID = ?", (1,))

        # Check Evakuerte insert call
        evakuert_insert_query = """
            INSERT INTO Evakuerte (Fornavn, MellomNavn, Etternavn, Adresse, Telefonnummer, KriseID)
            OUTPUT INSERTED.EvakuertID
            VALUES (?, ?, ?, ?, ?, ?);
            """
        mock_cursor.execute.assert_any_call(evakuert_insert_query, ("Test", "Middle", "User", "123 Test St", "12345678", 1))

        # Check KontaktPerson insert call
        kontakt_insert_query = """
                INSERT INTO KontaktPerson (Fornavn, MellomNavn, Etternavn, Telefonnummer, EvakuertID)
                VALUES (?, ?, ?, ?, ?);
            """
        mock_cursor.execute.assert_any_call(kontakt_insert_query, ("Kontakt", "", "Person", "87654321", 123))

        # Check Status insert call
        status_insert_query = "INSERT INTO Status ([Status], Lokasjon, EvakuertID) VALUES (?, ?, ?)"
        mock_cursor.execute.assert_any_call(status_insert_query, ("Evakuert", "Evakueringssenter A", 123))

        self.assertEqual(mock_conn.commit.call_count, 2) # Two commits: after KontaktPerson, and after Status
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
