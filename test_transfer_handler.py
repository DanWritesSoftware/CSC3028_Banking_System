"""
Unit tests for the transfer handler module.
Verifies transfer validation and database interactions.
"""

import unittest
from unittest.mock import Mock
from transfer_handler import Transfer


class TestTransferHandler(unittest.TestCase):
    """Test cases for the Transfer transaction handler."""

    def setUp(self):
        """Initialize test fixtures."""
        self.mock_db = Mock()
        self.valid_from = "1111111111"
        self.valid_to = "2222222222"
        self.valid_amount = 300.0

    def test_valid_transfer(self):
        """Test transfer with valid inputs should succeed."""
        self.mock_db.withdraw_from_account.return_value = []
        self.mock_db.deposit_to_account.return_value = []
        transfer = Transfer(self.valid_from, self.valid_to, self.valid_amount, self.mock_db)
        errors = transfer.try_transfer()
        self.assertEqual(errors, [])
        self.mock_db.withdraw_from_account.assert_called_once_with(
            self.valid_from, self.valid_amount)
        self.mock_db.deposit_to_account.assert_called_once_with(
            self.valid_to, self.valid_amount)

    def test_invalid_source_account(self):
        """Test transfer with invalid source account format should fail."""
        transfer = Transfer("bad_acc", self.valid_to, self.valid_amount, self.mock_db)
        errors = transfer.try_transfer()
        self.assertIn("Invalid source account number", errors)
        self.mock_db.withdraw_from_account.assert_not_called()

    def test_invalid_destination_account(self):
        """Test transfer with invalid destination account format should fail."""
        transfer = Transfer(self.valid_from, "bad_acc", self.valid_amount, self.mock_db)
        errors = transfer.try_transfer()
        self.assertIn("Invalid destination account number", errors)
        self.mock_db.withdraw_from_account.assert_not_called()

    def test_invalid_amount(self):
        """Test transfer with non-numeric amount should fail."""
        transfer = Transfer(self.valid_from, self.valid_to, "three hundred", self.mock_db)
        errors = transfer.try_transfer()
        self.assertIn("Invalid transfer amount (must be positive with ≤ 2 decimals)", errors)
        self.mock_db.withdraw_from_account.assert_not_called()

    def test_withdrawal_failure(self):
        """Test transfer with insufficient funds should fail."""
        self.mock_db.withdraw_from_account.return_value = ["Insufficient funds"]
        transfer = Transfer(self.valid_from, self.valid_to, 500.0, self.mock_db)
        errors = transfer.try_transfer()
        self.assertIn("Insufficient funds", errors)
        self.mock_db.deposit_to_account.assert_not_called()

    def test_deposit_failure_after_successful_withdrawal(self):
        """Test transfer where deposit fails after successful withdrawal."""
        self.mock_db.withdraw_from_account.return_value = []
        self.mock_db.deposit_to_account.return_value = ["Account not found"]
        transfer = Transfer(self.valid_from, "3333333333", 200.0, self.mock_db)
        errors = transfer.try_transfer()
        self.assertIn("Account not found", errors)
        self.mock_db.withdraw_from_account.assert_called()
        self.mock_db.deposit_to_account.assert_called()

if __name__ == '__main__':
    unittest.main()
