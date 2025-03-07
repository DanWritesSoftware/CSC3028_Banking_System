"""
withdrawal_handler.py
This module defines the Withdrawal class, which handles taking funds from an account.
"""

class Withdrawal:
    """
    Handles Withdrawing funds from an account.
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

    def try_withdrawal(self):
        """
        Attempts to withdraw funds from an account.
        Returns a list of error messages if the withdrawal fails.
        """
        output = []
        withdraw_errors = []

        withdraw_errors = self.database.withdraw_from_account(self.from_id, self.withdrawal_amount)

        if not withdraw_errors:
            return []
        else:
            for error in withdraw_errors:
                output.append(error)

        return output
