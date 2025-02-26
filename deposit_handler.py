"""
deposit_handler.py
This module defines the Deposit class, which handles transferring funds to an account.
"""

class Deposit:
    """
    Handles Depositing funds to an account.
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

    def try_deposit(self):
        """
        Attempts to deposit funds to an account.
        Returns a list of error messages if the transfer fails.
        """
        output = []
        deposit_errors = []

        deposit_errors = self.database.deposit_to_account(self.to_id, self.deposit_amount)

        if not deposit_errors:
            return []
        else:
            for error in deposit_errors:
                output.append(error)

        return output
