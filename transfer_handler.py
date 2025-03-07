"""
transfer_handler.py
This module defines the Transfer class, which handles transferring funds between accounts.
"""

class Transfer:
    """
    Handles transferring funds between accounts.
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

    def try_transfer(self):
        """
        Attempts to transfer funds between accounts.
        Returns a list of error messages if the transfer fails.
        """
        output = []
        withdraw_errors = []
        deposit_errors = []

        withdraw_errors = self.database.withdraw_from_account(self.from_id, self.transfer_amount)

        if not withdraw_errors:
            deposit_errors = self.database.deposit_to_account(self.to_id, self.transfer_amount)

        if not withdraw_errors and not deposit_errors:
            return []
        else:
            for error in withdraw_errors:
                output.append(error)
            for error in deposit_errors:
                output.append(error)

        return output
