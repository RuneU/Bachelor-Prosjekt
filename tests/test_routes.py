import unittest
import sys
import os
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

class FlaskRoutesTestCase(unittest.TestCase):
    def setUp(self):
        """Set up the test client."""
        self.app = app.test_client()
        self.app.testing = True
        
        # Create a test session context
        with self.app.session_transaction() as sess:
            sess['user_id'] = 1  # Simulate logged in user
            sess['lang'] = 'no'  # Set default language
        
        # Patch the login_required decorator
        self.patcher = patch('blueprints.auth.auth.login_required')
        self.mock_login_required = self.patcher.start()
        # Make the decorator just return the function unchanged
        self.mock_login_required.side_effect = lambda f: f

    def tearDown(self):
        """Clean up after each test."""
        self.patcher.stop()

    def test_index_route(self):
        """Test if '/' returns the correct page with expected content."""
        # We'll test for a 200 response and that it contains 'ExitNode'
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        # Check for something we know should be on the index page
        self.assertIn(b'ExitNode', response.data)
        # Check for some expected HTML structure
        self.assertIn(b'<html', response.data)
        self.assertIn(b'</html>', response.data)

    def test_set_user_id_route(self):
        """Test if '/set_user_id' correctly handles POST requests."""
        # Test valid ID
        response_valid = self.app.post('/set_user_id', 
                                json={"evakuert_id": "123"})
        self.assertEqual(response_valid.status_code, 200)
        self.assertIn(b'User ID stored successfully', response_valid.data)
        
        # Test invalid ID - non-digit
        response_invalid = self.app.post('/set_user_id', 
                                json={"evakuert_id": "abc"})
        self.assertEqual(response_invalid.status_code, 400)
        self.assertIn(b'Invalid Evakuert ID', response_invalid.data)

    @patch('app.render_template')
    @patch('blueprints.auth.auth.login_required', lambda f: f)  # Extra patch for nested decorators
    def test_admin_page_route(self, mock_render):
        """Test if '/admin_page' returns admin page with correct template."""
        mock_render.return_value = "Admin Page Content"
        
        response = self.app.get('/admin_page')
        self.assertEqual(response.status_code, 200)
        
        # Verify render_template was called with the correct template
        mock_render.assert_called_with('admin_page.html', t=unittest.mock.ANY, lang=unittest.mock.ANY)

    @patch('app.render_template')
    @patch('app.fetch_all_kriser')
    @patch('app.search_krise')
    @patch('blueprints.auth.auth.login_required', lambda f: f)  # Extra patch for nested decorators
    def test_admin_status_inc_route(self, mock_search, mock_fetch, mock_render):
        """Test if '/admin_status_inc' returns page with correct template."""
        mock_fetch.return_value = []
        mock_search.return_value = []
        mock_render.return_value = "Admin Status Inc Content"
        
        response = self.app.get('/admin_status_inc')
        self.assertEqual(response.status_code, 200)
        
        # Verify render_template was called with the correct template
        self.assertTrue(mock_render.called)
        args, kwargs = mock_render.call_args
        self.assertEqual(args[0], 'admin_status_inc.html')
        self.assertIn('krise_list', kwargs)

    @patch('app.render_template')
    def test_evacuee_search_get_route(self, mock_render):
        """Test if '/evacuee-search' GET returns search page template."""
        mock_render.return_value = "Evacuee Search Page Content"
        
        response = self.app.get('/evacuee-search')
        self.assertEqual(response.status_code, 200)
        
        # Verify render_template was called with the correct template
        mock_render.assert_called_with('evacuee_search.html', t=unittest.mock.ANY, lang=unittest.mock.ANY)

    @patch('app.connection_def')
    def test_evacuee_search_post_route_valid_id(self, mock_conn):
        """Test if '/evacuee-search' POST with valid ID redirects correctly."""
        # Mock database connection and cursor
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)  # 1 record found
        
        response = self.app.post('/evacuee-search', data={"evakuertID": "123"}, 
                                follow_redirects=False)
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/evacuee-update/123')

    # Fixed test for evacuee-update route
    @patch('blueprints.evacuee_update.routes.render_template')
    def test_evacuee_update_route(self, mock_render):
        """Test if '/evacuee-update/<id>' route exists and returns 200 status."""
        # Mock the render_template function in the evacuee_update blueprint
        mock_render.return_value = "Mocked Evacuee Update Page"
        
        # The route is likely implemented in the evacuee_update blueprint
        # We're testing that it responds, not the exact content
        response = self.app.get('/evacuee-update/123')
        self.assertEqual(response.status_code, 200)
        
        # Testing that the route exists and returns some string containing the ID
        self.assertTrue(any(str(123).encode() in response.data or b"123" in response.data))

    @patch('app.render_template')
    def test_newuser_route(self, mock_render):
        """Test if '/newuser' returns the template."""
        mock_render.return_value = "Newuser Page Content"
        
        response = self.app.get('/newuser')
        self.assertEqual(response.status_code, 200)
        
        # Verify render_template was called with the correct template
        mock_render.assert_called_with('newuser.html')

if __name__ == '__main__':
    unittest.main()