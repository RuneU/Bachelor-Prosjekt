import unittest
from unittest.mock import patch, MagicMock
from flask import session
from app import app
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestIncidentCreation(unittest.TestCase):
    def setUp(self):
        """Set up test client and configure app for testing."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.client = app.test_client()
        self.client.testing = True
        
        # Create session context for testing routes requiring login
        with self.client.session_transaction() as sess:
            sess['user_id'] = '12345'  # Mock user login
            sess['admin'] = True
            sess['lang'] = 'no'
    
    @patch('blueprints.incident_creation.routes.create_krise')
    def test_handle_incident_success(self, mock_create_krise):
        """Test successful incident creation."""
        # Configure the mock to return True (successful creation)
        mock_create_krise.return_value = True
        
        # Test data for incident creation
        test_data = {
            'krise-status': 'Ny krise',
            'krise-type': 'Brann',
            'krise-navn': 'Test Incident',
            'krise-lokasjon': 'Oslo',
            'annen-info': 'This is a test incident'
        }
        
        # Send POST request to the incident creation handler
        response = self.client.post('/handle_incident', data=test_data, follow_redirects=True)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        
        # Check that create_krise was called with the correct arguments
        mock_create_krise.assert_called_once_with(
            'Ny krise', 'Brann', 'Test Incident', 'Oslo', 'This is a test incident'
        )
    
    @patch('blueprints.incident_creation.routes.create_krise')
    def test_handle_incident_missing_fields(self, mock_create_krise):
        """Test incident creation with missing required fields."""
        # Test data with missing fields
        test_data = {
            'krise-status': 'Ny krise',
            'krise-type': '',  # Missing type
            'krise-navn': 'Test Incident',
            'krise-lokasjon': '',  # Missing location
            'annen-info': 'This is a test incident'
        }
        
        # Send POST request to the incident creation handler
        response = self.client.post('/handle_incident', data=test_data, follow_redirects=True)
        
        # Verify redirect occurred
        self.assertEqual(response.status_code, 200)
        
        # Verify create_krise was not called
        mock_create_krise.assert_not_called()
    
    @patch('blueprints.incident_creation.routes.create_krise')
    def test_handle_incident_failure(self, mock_create_krise):
        """Test incident creation when DB operation fails."""
        # Configure the mock to return False (failed creation)
        mock_create_krise.return_value = False
        
        # Test data for incident creation
        test_data = {
            'krise-status': 'Ny krise',
            'krise-type': 'Brann',
            'krise-navn': 'Test Incident',
            'krise-lokasjon': 'Oslo',
            'annen-info': 'This is a test incident'
        }
        
        # Send POST request to the incident creation handler
        response = self.client.post('/handle_incident', data=test_data, follow_redirects=True)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        
        # Verify create_krise was called
        mock_create_krise.assert_called_once()
    
    @patch('blueprints.incident_creation.routes.create_krise')
    def test_handle_incident_exception(self, mock_create_krise):
        """Test incident creation when an exception occurs."""
        # Configure the mock to raise an exception
        mock_create_krise.side_effect = Exception("Database error")
        
        # Test data for incident creation
        test_data = {
            'krise-status': 'Ny krise',
            'krise-type': 'Brann',
            'krise-navn': 'Test Incident',
            'krise-lokasjon': 'Oslo',
            'annen-info': 'This is a test incident'
        }
        
        # Send POST request to the incident creation handler
        response = self.client.post('/handle_incident', data=test_data, follow_redirects=True)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        
        # Verify create_krise was called
        mock_create_krise.assert_called_once()
    
    def test_incident_creation_page_load(self):
        """Test that the incident creation page loads correctly."""
        response = self.client.get('/incident_creation')
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        
        # Check for expected content in the response
        # The actual rendered content has "Informasjon om Hendelsen" (the Norwegian translation)
        # instead of the translation key
        self.assertIn(b'Informasjon om Hendelsen', response.data)
        
    def test_incident_creation_unauthorized(self):
        """Test that unauthorized users cannot access the incident creation page."""
        # Create a new client without login session
        client = app.test_client()
        
        # Try to access the incident creation page
        response = client.get('/incident_creation', follow_redirects=True)
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login', response.data.lower())


if __name__ == '__main__':
    unittest.main()