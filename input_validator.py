"""
Module for handling input validation in the banking system.
"""

import re

class InputValidator:
    """
    A class to handle input validation for the banking system.
    """

    @staticmethod
    def validate_account_number(account_number: str) -> bool:
        """
        Validates account numbers.
        Rules:
        - Must be a string of exactly 10 digits.
        """
        if not isinstance(account_number, str):
            return False
        if len(account_number) != 10:
            return False
        if not account_number.isdigit():
            return False
        return True

    @staticmethod
    def validate_currency_amount(amount: float) -> bool:
        """
        Validates currency amounts.
        Rules:
        - Must be a positive number (greater than zero).
        - Must have up to 2 decimal places.
        """
        if not isinstance(amount, (int, float)):
            return False
        if amount <= 0:  # Changed to check for positive (> 0), not just non-negative (>= 0)
            return False
        if not round(amount, 2) == amount:
            return False
        return True

    @staticmethod
    def validate_transaction_limit(limit: float) -> bool:
        """
        Validates transaction limits.
        Rules:
        - Must be a positive number.
        - Must not exceed system-defined maximum limits.
        """
        max_limit = 10000  # Example maximum limit
        if not isinstance(limit, (int, float)):
            return False
        if limit < 0 or limit > max_limit:
            return False
        return True

    @staticmethod
    def validate_password_complexity(password: str) -> bool:
        """
        Validates password complexity.
        Rules:
        - At least 8 characters.
        - At least one uppercase letter.
        - At least one lowercase letter.
        - At least one digit.
        - At least one special character.
        """
        if len(password) < 8:
            return False
        if not any(char.isupper() for char in password):
            return False
        if not any(char.islower() for char in password):
            return False
        if not any(char.isdigit() for char in password):
            return False
        if not any(char in "!@#$%^&*()" for char in password):
            return False
        return True

    @staticmethod
    def validate_username(username: str) -> bool:
        """
        Validates usernames.
        Rules:
        - Must be alphanumeric.
        - Must be between 5 and 20 characters.
        """
        if not isinstance(username, str):
            return False
        if not username.isalnum():
            return False
        if len(username) < 5 or len(username) > 20:
            return False
        return True

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validates email addresses.
        Rules:
        - Must follow standard email format (e.g., user@domain.com).
        """
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_role(role: str) -> bool:
        """
        Validates user roles.
        Rules:
        - Must be one of the predefined roles: Admin, Teller, Customer.
        """
        return role in ["Admin", "Teller", "Customer"]
