"""
temp_account_holder.py
This module defines the AccountHolder class, which manages a collection of accounts.
"""

from Account import Account

class AccountHolder:
    """
    Manages a collection of accounts.
    Provides functionality to add new accounts and store account details.
    """

    def __init__(self):
        """Initializes the AccountHolder with a few default accounts."""
        self.contents = []
        self.account_number = 0
        self.contents.append(Account(1, 'Savings', 32.0))
        self.contents.append(Account(2, 'Checking', 350.0))
        self.contents.append(Account(3, 'Investment', 50000000.0))

    def add_account(self, account_name: str, balance: float):
        """
        Adds a new account to the account holder's collection.

        Args:
            account_name (str): The name of the account (e.g., 'Savings', 'Checking').
            balance (float): The initial balance of the account.
        """
        self.account_number += 1
        self.contents.append(Account(self.account_number, account_name, balance))
