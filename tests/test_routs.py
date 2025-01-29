import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

class FlaskRoutesTestCase(unittest.TestCase):
    def setUp(self):
        """Set up the test client."""
        self.app = app.test_client()
        self.app.testing = True

    def test_index_route(self):
        """Test if '/' and '/index' return the correct page."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Velkommen til Gruppe 4 sitt prosjekt', response.data)  # Check actual content

    def test_register_route(self):
        """Test if '/register' returns the correct page."""
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registrering', response.data)  # Check actual content

    def test_admin_route(self):
        """Test if '/admin' returns the correct page."""
        response = self.app.get('/admin')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Side', response.data)  # Check actual content

if __name__ == '__main__':
    unittest.main()
