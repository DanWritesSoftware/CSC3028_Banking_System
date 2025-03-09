"""
deposit_handler.py
This module defines the Deposit class, which handles depositing funds to an account.
"""

from input_validator import InputValidator

class Deposit:
    """
    Handles depositing funds to an account with input validation.
    Manages the depositing process and returns any errors encountered.
    """

    def __init__(self, to_id: str, deposit_amount: float, database):
        """
        Initializes the Deposit object.

        Args:
            from_id (str): The ID of the account to deposit funds to.
            deposit_amount (float): The amount to transfer.
            database: The database handler for account operations.
        """
        self.to_id = to_id
        self.deposit_amount = deposit_amount
        self.database = database

    def try_deposit(self) -> list[str]:
        """
        Attempt deposit after validating inputs.
        Returns a list of error messages if the transfer fails.
        """
        errors = []

        # Validate account number
        if not InputValidator.validate_account_number(self.to_id):
            errors.append("Invalid account number")

        # Validate deposit amount
        if not InputValidator.validate_currency_amount(self.deposit_amount):
            errors.append("Invalid deposit amount (must be positive with ≤ 2 decimals)")

        if errors:
            return errors

        # Proceed with database operation
        return self.database.deposit_to_account(self.to_id, self.deposit_amount)
