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
        # Updated to mock the transfer_funds_by_account_number method
        self.mock_db.transfer_funds_by_account_number.return_value = []
        transfer = Transfer(self.valid_from, self.valid_to, self.valid_amount, self.mock_db)
        errors = transfer.try_transfer()
        self.assertEqual(errors, [])
        # Updated assertion to check the correct method is called
        self.mock_db.transfer_funds_by_account_number.assert_called_once_with(
            from_account_id=self.valid_from, 
            to_account_id=self.valid_to, 
            amount=self.valid_amount)

    def test_invalid_source_account(self):
        """Test transfer with invalid source account format should fail."""
        transfer = Transfer("bad_acc", self.valid_to, self.valid_amount, self.mock_db)
        errors = transfer.try_transfer()
        self.assertIn("Invalid source account number", errors)
        self.mock_db.transfer_funds_by_account_number.assert_not_called()

    def test_invalid_destination_account(self):
        """Test transfer with invalid destination account format should fail."""
        transfer = Transfer(self.valid_from, "bad_acc", self.valid_amount, self.mock_db)
        errors = transfer.try_transfer()
        self.assertIn("Invalid destination account number", errors)
        self.mock_db.transfer_funds_by_account_number.assert_not_called()

    def test_invalid_amount(self):
        """Test transfer with non-numeric amount should fail."""
        transfer = Transfer(self.valid_from, self.valid_to, "three hundred", self.mock_db)
        errors = transfer.try_transfer()
        self.assertIn("Invalid transfer amount (must be positive with ≤ 2 decimals)", errors)
        self.mock_db.transfer_funds_by_account_number.assert_not_called()

    def test_withdrawal_failure(self):
        """Test transfer with insufficient funds should fail."""
        # Updated to mock the transfer method with an error response
        self.mock_db.transfer_funds_by_account_number.return_value = ["Error: Insufficient Funds, Brokie."]
        transfer = Transfer(self.valid_from, self.valid_to, 500.0, self.mock_db)
        errors = transfer.try_transfer()
        self.assertIn("Error: Insufficient Funds, Brokie.", errors)

    def test_deposit_failure_after_successful_withdrawal(self):
        """Test transfer where destination account is not found."""
        # Updated to mock transfer with destination account error
        self.mock_db.transfer_funds_by_account_number.return_value = ["Error: Destination Account Not Found"]
        transfer = Transfer(self.valid_from, "3333333333", 200.0, self.mock_db)
        errors = transfer.try_transfer()
        self.assertIn("Error: Destination Account Not Found", errors)
        self.mock_db.transfer_funds_by_account_number.assert_called()

if __name__ == '__main__':
    unittest.main()
