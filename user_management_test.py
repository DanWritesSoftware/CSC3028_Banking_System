"""
user_management_test.py
This module contains unit tests for the UserManager class.
"""

import unittest
from unittest.mock import patch
from user_management import UserManager

class TestUserManager(unittest.TestCase):
    """
    Test cases for the UserManager class.
    Tests include user signup, login, and 2FA functionality.
    """

    def setUp(self):
        """
        Set up the UserManager instance for each test case.
        """
        self.um = UserManager()

    def test_signup_success(self):
        """
        Test successful user signup with valid inputs.
        """
        result = self.um.sign_up_customer("validUser", "valid@example.com", "StrongPass1!", "StrongPass1!")
        self.assertEqual(result, "User registered successfully!")

    def test_signup_mismatched_passwords(self):
        """
        Test user signup with mismatched passwords.
        """
        result = self.um.sign_up_customer("validUser", "valid@example.com", "StrongPass1!", "WrongPass!")
        self.assertEqual(result, "Passwords do not match.")

    @patch('user_management.UserManager._send_verification_email')
    def test_login_success_triggers_2fa(self, mock_send_email):
        """
        Test successful login triggers 2FA email.
        """
        # Setup: Create a test user
        self.um.sign_up_customer("testUser", "test@example.com", "TestPass1!", "TestPass1!")

        # Test login
        result = self.um.login("testUser", "TestPass1!")

        # Verify 2FA flow
        self.assertTrue(result['requires_2fa'])
        self.assertEqual(result['email'], "test@example.com")
        mock_send_email.assert_called_once()

    def test_login_invalid_user(self):
        """
        Test login with invalid credentials.
        """
        result = self.um.login("invalidUser", "WrongPass!")
        self.assertIsNone(result)

    @patch('user_management.UserManager._generate_verification_code')
    @patch('user_management.UserManager._send_verification_email')
    def test_verify_2fa_success(self, mock_send_email, mock_generate_code):
        """
        Test successful 2FA verification.
        """
        # Setup: Create a test user and mock the verification code
        self.um.sign_up_customer("testUser", "test@example.com", "TestPass1!", "TestPass1!")
        mock_generate_code.return_value = "123456"  # Mock the code

        # Mock the email sending to avoid actual email delivery
        mock_send_email.return_value = True

        # Trigger login to generate the 2FA code
        login_result = self.um.login("testUser", "TestPass1!")
        self.assertTrue(login_result['requires_2fa'])

        # Test verification
        result = self.um.verify_2fa("test@example.com", "123456")
        self.assertIsNotNone(result)
        self.assertEqual(result['usrName'], "testUser")

    def test_verify_2fa_invalid_code(self):
        """
        Test 2FA verification with invalid code.
        """
        # Setup: Create a test user
        self.um.sign_up_customer("testUser", "test@example.com", "TestPass1!", "TestPass1!")

        # Test verification with wrong code
        result = self.um.verify_2fa("test@example.com", "000000")
        self.assertIsNone(result)

    @patch('user_management.UserManager._generate_verification_code')
    @patch('user_management.time.time')
    def test_verify_2fa_expired_code(self, mock_time, mock_generate_code):
        """
        Test 2FA verification with expired code.
        """
        # Setup: Create a test user
        self.um.sign_up_customer("testUser", "test@example.com", "TestPass1!", "TestPass1!")
        mock_generate_code.return_value = "123456"
        mock_time.return_value = 0  # Initial time at epoch

        # Trigger login to generate the 2FA code
        self.um.login("testUser", "TestPass1!")

        # Simulate time passing beyond expiration
        mock_time.return_value = 301

        # Test verification
        result = self.um.verify_2fa("test@example.com", "123456")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
