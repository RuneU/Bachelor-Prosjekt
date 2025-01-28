import os
import sys
import unittest
from flask import Flask
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app  # Replace "your_flask_app" with your actual Flask app file

class TestFlaskRoutes(unittest.TestCase):
    def setUp(self):
        # Create a test client for your Flask app
        self.app = app.test_client()
        self.app.testing = True  # Enable testing mode

    def test_home_route(self):
        # Test if the "home" route (/) works
        response = self.app.get('/index')
        self.assertEqual(response.status_code, 200)  # Check if the "door" opens (status 200 = OK)
        self.assertIn(b'Welcome', response.data)  # Check if the word "Welcome" is on the page

if __name__ == '__main__':
    unittest.main()