"""
database_handler.py
This module handles database operations for the banking system.
"""

import sqlite3
from account import Account

class Database:
    """
    Handles database operations for the banking system.
    Manages user accounts, authentication, and transactions.
    """

    def __init__(self, name):
        self.name = name

    def create_account(self, acc_id: str, usr_id: str, acc_name: str, acc_balance: float) -> bool:
        """Creates a new account in the database."""
        connection = sqlite3.connect(self.name, check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO Account (accID, accType, accUserID, accValue) VALUES (?, ?, ?, ?)",
            (acc_id, acc_name, usr_id, acc_balance)
        )
        connection.commit()
        connection.close()
        return True

    def create_user(self, usr_id: int, usr_name: str, email: str, password: str) -> bool:
        """Creates a new user in the database."""
        connection = sqlite3.connect(self.name, check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO User (usrID, usrName, email, password) VALUES (?, ?, ?, ?)",
            (usr_id, usr_name, email, password)
        )
        connection.commit()
        connection.close()
        return True

    def get_user_accounts(self, usr_id: str) -> list[Account]:
        """Retrieves all accounts for a given user ID."""
        connection = sqlite3.connect(self.name, check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM Account WHERE accUserID=?", (usr_id,))
        rows = cursor.fetchall()

        accounts = []
        for row in rows:
            acc_id = row[0]
            acc_value = row[1]
            acc_type = row[2]
            accounts.append(Account(acc_id, acc_type, acc_value))

        connection.close()
        return accounts

    def get_users(self, usr_id: str) -> list[dict]:
        """Retrieves user data by user ID."""
        connection = sqlite3.connect(self.name, check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM User WHERE usrID=?", (usr_id,))
        rows = cursor.fetchall()

        users = []
        for row in rows:
            users.append({
                "usrID": row[0],
                "usrName": row[1],
                "email": row[2],
                "password": row[3]
            })

        connection.close()
        return users

    def user_login(self, user_name: str, password: str) -> dict | None:
        """Authenticates a user and returns their data if successful."""
        connection = sqlite3.connect(self.name, check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM User WHERE usrName=? AND password=?",
            (user_name, password)
        )
        row = cursor.fetchone()

        connection.close()

        if row:
            return {
                "usrID": row[0],
                "usrName": row[1],
                "email": row[2],
                "password": row[3]
            }
        return None

    def account_id_in_use(self, random_id: str) -> bool:
        """Returns True if the account ID is in use."""
        connection = sqlite3.connect(self.name, check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM Account WHERE accID=?", (random_id,))
        rows = cursor.fetchall()

        connection.close()
        return bool(rows)

    def user_id_in_use(self, random_id: str) -> bool:
        """Returns True if the user ID is in use."""
        connection = sqlite3.connect(self.name, check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM User WHERE usrID=?", (random_id,))
        rows = cursor.fetchall()

        connection.close()
        return bool(rows)

    def withdraw_from_account(self, account_id: str, amount: float) -> list[str]:
        """Withdraws funds from an account."""
        connection = sqlite3.connect(self.name, check_same_thread=False)
        cursor = connection.cursor()

        output = []
        cursor.execute("SELECT accValue FROM Account WHERE accID=?", (account_id,))
        result = cursor.fetchone()

        if result:
            value = float(result[0])  # Ensure value is treated as float
        else:
            output.append("Error: Withdrawal Account not found")
            connection.close()
            return output

        if value < amount:
            output.append("Error: Insufficient Funds")
        else:
            new_value = value - amount
            cursor.execute(
                "UPDATE Account SET accValue=? WHERE accID=?",
                (new_value, account_id)
            )
            connection.commit()

        connection.close()
        return output

    def deposit_to_account(self, account_id: str, amount: float) -> list[str]:
        """Deposits funds into an account."""
        if amount <= 0:
            return ["Error: Deposit amount must be greater than zero"]

        connection = sqlite3.connect(self.name, check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("SELECT accValue FROM Account WHERE accID=?", (account_id,))
        result = cursor.fetchone()

        if result:
            value = float(result[0])  # Ensure value is treated as float
        else:
            connection.close()
            return ["Error: Depositing Account not found"]

        new_value = value + amount
        cursor.execute(
            "UPDATE Account SET accValue=? WHERE accID=?",
            (new_value, account_id)
        )
        connection.commit()

        connection.close()
        return []

    def password_reset(self, user_name: str, email: str, password: str) -> bool:
        """Resets a user's password."""
        connection = sqlite3.connect(self.name, check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute(
            "UPDATE User SET password=? WHERE usrName=? AND email=?",
            (password, user_name, email)
        )
        connection.commit()
        connection.close()
        return True

    def get_user_by_username(self, username: str) -> dict | None:
        """Retrieves user data by username."""
        connection = sqlite3.connect(self.name, check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM User WHERE usrName=?", (username,))
        row = cursor.fetchone()

        connection.close()

        if row:
            return {
                "usrID": row[0],
                "usrName": row[1],
                "email": row[2],
                "password": row[3]
            }
        return None

    def get_user_by_email(self, email: str) -> dict | None:
        """Retrieves user by email."""
        connection = sqlite3.connect(self.name, check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM User WHERE email=?", (email,))
        row = cursor.fetchone()
        connection.close()

        if row:
            return {
                "usrID": row[0],
                "usrName": row[1],
                "email": row[2],
                "password": row[3]
            }
        return None
