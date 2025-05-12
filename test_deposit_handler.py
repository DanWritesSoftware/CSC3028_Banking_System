"""
Unit tests for the deposit handler module.
Verifies deposit validation and database interactions.
"""

import unittest
from unittest.mock import Mock, patch
from deposit_handler import Deposit
from input_validator import InputValidator


class TestDepositHandler(unittest.TestCase):
    """Test cases for the Deposit transaction handler."""

    def setUp(self):
        """Initialize test fixtures."""
        self.mock_db = Mock()
        self.valid_account = "0987654321"
        self.valid_amount = 200.0

    def test_valid_deposit(self):
        """Test deposit with valid inputs should succeed."""
        self.mock_db.deposit_to_account.return_value = []
        deposit = Deposit(self.valid_account, self.valid_amount, self.mock_db)
        errors = deposit.try_deposit()
        self.assertEqual(errors, [])
        self.mock_db.deposit_to_account.assert_called_once_with(
            self.valid_account, self.valid_amount)

    def test_invalid_account_number(self):
        """Test deposit with invalid account format should fail."""
        # No need to configure the mock since validation will fail
        deposit = Deposit("short", self.valid_amount, self.mock_db)
        errors = deposit.try_deposit()
        self.assertIn("Invalid account number", errors)
        self.mock_db.deposit_to_account.assert_not_called()

    def test_zero_amount(self):
        """Test deposit with zero amount should fail."""
        # No need to configure the mock since validation will fail
        deposit = Deposit(self.valid_account, 0.0, self.mock_db)
        errors = deposit.try_deposit()
        self.assertIn("Invalid deposit amount (must be positive with ≤ 2 decimals)", errors)
        self.mock_db.deposit_to_account.assert_not_called()

    def test_non_numeric_amount(self):
        """Test deposit with non-numeric amount should fail."""
        # No need to configure the mock since validation will fail
        deposit = Deposit(self.valid_account, "two hundred", self.mock_db)
        errors = deposit.try_deposit()
        self.assertIn("Invalid deposit amount (must be positive with ≤ 2 decimals)", errors)
        self.mock_db.deposit_to_account.assert_not_called()

    def test_database_error(self):
        """Test database error during deposit should propagate."""
        self.mock_db.deposit_to_account.return_value = ["Account not found"]
        deposit = Deposit("1111111111", 300.0, self.mock_db)
        errors = deposit.try_deposit()
        self.assertIn("Account not found", errors)

if __name__ == '__main__':
    unittest.main()
