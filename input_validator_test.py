"""
Unit tests for the InputValidator class in the input_validator module.
"""

import unittest
from input_validator import InputValidator

class TestInputValidator(unittest.TestCase):
    """
    Unit tests for the InputValidator class.
    """

    def test_validate_account_number(self):
        """Test validation of account numbers."""
        self.assertTrue(InputValidator.validate_account_number("1234567890"))
        self.assertTrue(InputValidator.validate_account_number("9876543210"))
        self.assertFalse(InputValidator.validate_account_number("12345"))  # Too short
        self.assertFalse(InputValidator.validate_account_number("123456789a"))  # Contains non-digit
        self.assertFalse(InputValidator.validate_account_number("12345678901"))  # Too long
        self.assertFalse(InputValidator.validate_account_number(""))  # Empty string

    def test_validate_currency_amount(self):
        """Test validation of currency amounts."""
        self.assertTrue(InputValidator.validate_currency_amount(100.00))
        self.assertTrue(InputValidator.validate_currency_amount(0.01))
        self.assertTrue(InputValidator.validate_currency_amount(9999.99))
        self.assertFalse(InputValidator.validate_currency_amount(-100.00))  # Negative
        self.assertFalse(InputValidator.validate_currency_amount(100.001)) # Too many decimal places
        self.assertFalse(InputValidator.validate_currency_amount("100.00"))  # Wrong type
        self.assertFalse(InputValidator.validate_currency_amount(None))  # None

    def test_validate_transaction_limit(self):
        """Test validation of transaction limits."""
        self.assertTrue(InputValidator.validate_transaction_limit(5000))
        self.assertTrue(InputValidator.validate_transaction_limit(10000))
        self.assertFalse(InputValidator.validate_transaction_limit(-100))  # Negative
        self.assertFalse(InputValidator.validate_transaction_limit(15000))  # Exceeds max limit
        self.assertFalse(InputValidator.validate_transaction_limit("1000"))  # Wrong type

    def test_validate_password_complexity(self):
        """Test validation of password complexity."""
        self.assertTrue(InputValidator.validate_password_complexity("Password1!"))
        self.assertTrue(InputValidator.validate_password_complexity("Secure123#"))
        self.assertFalse(InputValidator.validate_password_complexity("password")) # No Ucase/special
        self.assertFalse(InputValidator.validate_password_complexity("PASSWORD1!"))  # No lowercase
        self.assertFalse(InputValidator.validate_password_complexity("Password!"))  # No digit
        self.assertFalse(InputValidator.validate_password_complexity("Pass1"))  # Too short
        self.assertFalse(InputValidator.validate_password_complexity(""))  # Empty string

    def test_validate_username(self):
        """Test validation of usernames."""
        self.assertTrue(InputValidator.validate_username("testuser"))
        self.assertTrue(InputValidator.validate_username("user123"))
        self.assertFalse(InputValidator.validate_username("test"))  # Too short
        self.assertFalse(InputValidator.validate_username("test_user"))  # Contains underscore
        self.assertFalse(InputValidator.validate_username(""))  # Empty string

    def test_validate_email(self):
        """Test validation of email addresses."""
        self.assertTrue(InputValidator.validate_email("user@example.com"))
        self.assertTrue(InputValidator.validate_email("user.name+tag@domain.co"))
        self.assertFalse(InputValidator.validate_email("user@.com"))  # Missing domain
        self.assertFalse(InputValidator.validate_email("user@domain"))  # Missing top-level domain
        self.assertFalse(InputValidator.validate_email(""))  # Empty string

    def test_validate_role(self):
        """Test validation of user roles."""
        self.assertTrue(InputValidator.validate_role("Admin"))
        self.assertTrue(InputValidator.validate_role("Teller"))
        self.assertTrue(InputValidator.validate_role("Customer"))
        self.assertFalse(InputValidator.validate_role("Manager"))  # Not a valid role
        self.assertFalse(InputValidator.validate_role(""))  # Empty string


if __name__ == "__main__":
    unittest.main()
