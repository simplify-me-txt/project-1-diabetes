import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import tempfile
import sqlite3
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, init_db

class TestDiabetesApp(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.secret_key = 'test_secret'
        self.client = app.test_client()
        
        # Initialize test database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Create tables as defined in init_db (simplified or copied)
            # Or we can just try to run init_db with the patched connection
            pass

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    @patch('app.get_db_connection')
    def test_register_and_login(self, mock_get_db):
        # Setup mock connection to point to our temp db
        def get_test_db():
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
            
        mock_get_db.side_effect = get_test_db

        # Initialize DB
        with app.app_context():
            # We need to manually initialize because init_db calls get_db_connection
            # which we are mocking
            init_db()

        # Test Registration
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Password123!',
            'role': 'patient'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful', response.data)

        # Test Login
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'Password123!'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login successful', response.data)
        
        # Test Dashboard Access
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'testuser', response.data)

    @patch('app.get_db_connection')
    def test_prediction_endpoint(self, mock_get_db):
        def get_test_db():
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        mock_get_db.side_effect = get_test_db

        # Init DB and Login
        with app.app_context():
            init_db()
            
        # Register and Login first
        self.client.post('/register', data={
            'username': 'patient1',
            'email': 'p1@example.com',
            'password': 'Password123!',
            'role': 'patient'
        }, follow_redirects=True)
        
        self.client.post('/login', data={
            'username': 'patient1',
            'password': 'Password123!'
        }, follow_redirects=True)

        # Test Prediction (GET)
        response = self.client.get('/predict')
        self.assertEqual(response.status_code, 200)

        # Test Prediction (POST) - Valid Data
        # Note: This might require valid models to be loaded in app.py
        # If models are missing, app.py catches it and sets model=None
        # We should check if models are loaded.
        
        response = self.client.post('/predict', data={
            'pregnancies': '1',
            'glucose': '120',
            'blood_pressure': '70',
            'skin_thickness': '20',
            'insulin': '79',
            'bmi': '25.0',
            'dpf': '0.5',
            'age': '33'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        # Check for success message or result
        # If models are present, we expect a result.
        if b'ML model files not found' in response.data:
            print("Models not found, skipping prediction verification")
        else:
            self.assertIn(b'Prediction Result', response.data)

if __name__ == '__main__':
    unittest.main()
