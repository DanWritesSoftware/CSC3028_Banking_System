"""
Unit tests for the withdrawal handler module.
Verifies withdrawal validation and database interactions.
"""

import unittest
from unittest.mock import Mock
from withdrawal_handler import Withdrawal


class TestWithdrawalHandler(unittest.TestCase):
    """Test cases for the Withdrawal transaction handler."""

    def setUp(self):
        """Initialize test fixtures."""
        self.mock_db = Mock()
        self.valid_account = "1234567890"
        self.valid_amount = 100.0

    def test_valid_withdrawal(self):
        """Test withdrawal with valid inputs should succeed."""
        self.mock_db.withdraw_from_account.return_value = []
        withdrawal = Withdrawal(self.valid_account, self.valid_amount, self.mock_db)
        errors = withdrawal.try_withdrawal()
        self.assertEqual(errors, [])
        self.mock_db.withdraw_from_account.assert_called_once_with(
            self.valid_account, self.valid_amount)

    def test_invalid_account_number(self):
        """Test withdrawal with invalid account format should fail."""
        withdrawal = Withdrawal("invalid_acc", self.valid_amount, self.mock_db)
        errors = withdrawal.try_withdrawal()
        self.assertIn("Invalid account number", errors)
        self.mock_db.withdraw_from_account.assert_not_called()

    def test_negative_amount(self):
        """Test withdrawal with negative amount should fail."""
        withdrawal = Withdrawal(self.valid_account, -50.0, self.mock_db)
        errors = withdrawal.try_withdrawal()
        self.assertIn("Invalid withdrawal amount (must be positive with ≤ 2 decimals)", errors)
        self.mock_db.withdraw_from_account.assert_not_called()

    def test_too_many_decimals(self):
        """Test withdrawal with >2 decimal places should fail."""
        withdrawal = Withdrawal(self.valid_account, 123.456, self.mock_db)
        errors = withdrawal.try_withdrawal()
        self.assertIn("Invalid withdrawal amount (must be positive with ≤ 2 decimals)", errors)
        self.mock_db.withdraw_from_account.assert_not_called()

    def test_database_error(self):
        """Test database error during withdrawal should propagate."""
        self.mock_db.withdraw_from_account.return_value = ["Insufficient funds"]
        withdrawal = Withdrawal(self.valid_account, 500.0, self.mock_db)
        errors = withdrawal.try_withdrawal()
        self.assertIn("Insufficient funds", errors)

if __name__ == '__main__':
    unittest.main()
