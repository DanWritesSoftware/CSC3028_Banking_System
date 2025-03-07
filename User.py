"""
user.py
This module defines the User class for representing banking system users.
"""

class User:
    """Represents a user in the banking system with personal and authentication details."""

    def __init__(self, usr_id: str, usr_name: str, email: str, password: str):
        """
        Initialize a User instance.
        """
        self.usr_name = usr_name
        self.password = password
        self.usr_id = usr_id
        self.email = email

    def print_user_details(self) -> None:
        """Print basic user details to the console."""
        print(f"User Name: {self.usr_name}, Password: {self.password}")
