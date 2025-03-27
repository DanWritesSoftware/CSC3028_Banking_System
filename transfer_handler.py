"""
transfer_handler.py
This module defines the Transfer class, which handles transferring funds between accounts.
"""

from input_validator import InputValidator

class Transfer:
    """
    Handles transferring funds between accounts with input validation.
    Manages the transfer process and returns any errors encountered.
    """

    def __init__(self, from_id: str, to_id: str, transfer_amount: float, database):
        """
        Initializes the Transfer object.

        Args:
            from_id (str): The ID of the account to transfer funds from.
            to_id (str): The ID of the account to transfer funds to.
            transfer_amount (float): The amount to transfer.
            database: The database handler for account operations.
        """
        self.from_id = from_id
        self.to_id = to_id
        self.transfer_amount = transfer_amount
        self.database = database

    def try_transfer(self) -> list[str]:
        """
        Attempt transfer after validating inputs.
        Returns a list of error messages if the transfer fails.
        """
        errors = []

        # Validate account numbers
        if not InputValidator.validate_account_number(self.from_id):
            errors.append("Invalid source account number")
        if not InputValidator.validate_account_number(self.to_id):
            errors.append("Invalid destination account number")

        # Validate transfer amount
        if not InputValidator.validate_currency_amount(self.transfer_amount):
            errors.append("Invalid transfer amount (must be positive with ≤ 2 decimals)")

        if errors:
            return errors

        # Proceed with database operations
        withdraw_errors = self.database.withdraw_from_account(self.from_id, self.transfer_amount)
        if withdraw_errors:
            return withdraw_errors

        deposit_errors = self.database.deposit_to_account(self.to_id, self.transfer_amount)
        return deposit_errors
