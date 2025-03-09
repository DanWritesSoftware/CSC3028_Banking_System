"""
withdrawal_handler.py
This module defines the Withdrawal class, which handles withdrawing funds from an account.
"""

from input_validator import InputValidator

class Withdrawal:
    """
    Handles withdrawing funds from an account with input validation.
    Manages the Withdrawing process and returns any errors encountered.
    """

    def __init__(self, from_id: str, withdrawal_amount: float, database):
        """
        Initializes the Withdrawal object.

        Args:
            from_id (str): The ID of the account to withdraw funds from.
            withdrawal_amount (float): The amount withdraw.
            database: The database handler for account operations.
        """
        self.from_id = from_id
        self.withdrawal_amount = withdrawal_amount
        self.database = database

    def try_withdrawal(self) -> list[str]:
        """
        Attempt withdrawal after validating inputs.
        Returns a list of error messages if the withdrawal fails.
        """
        errors = []

        # Validate account number
        if not InputValidator.validate_account_number(self.from_id):
            errors.append("Invalid account number")

        # Validate withdrawal amount
        if not InputValidator.validate_currency_amount(self.withdrawal_amount):
            errors.append("Invalid withdrawal amount (must be positive with ≤ 2 decimals)")

        if errors:
            return errors

        # Proceed with database operation
        return self.database.withdraw_from_account(self.from_id, self.withdrawal_amount)
