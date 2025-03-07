"""
session_manager_test.py
This module contains unit tests for the SessionManager class.
"""

import unittest
from flask import Flask, session
from session_manager import SessionManager

class TestSessionManager(unittest.TestCase):
    """
    Test cases for the SessionManager class.
    Tests include user login and logout functionality.
    """

    def setUp(self):
        """
        Set up the Flask app and test client for each test case.
        """
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.secret_key = 'testkey'
        self.client = self.app.test_client()

    def test_login_user(self):
        """
        Test that the login_user method correctly sets user_id and username in the session.
        """
        with self.app.test_request_context():
            SessionManager.login_user(1, "testuser")
            self.assertEqual(session['user_id'], 1)
            self.assertEqual(session['username'], "testuser")

    def test_logout_user(self):
        """
        Test that the logout_user method removes user_id and username from the session.
        """
        with self.app.test_request_context():
            SessionManager.login_user(1, "testuser")
            SessionManager.logout_user()
            self.assertNotIn('user_id', session)

if __name__ == '__main__':
    unittest.main()
