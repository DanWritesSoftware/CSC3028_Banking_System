"""
database_handler.py
This module handles database operations for the banking system.
"""

import sqlite3
from Account import Account

class Database:
    """
    Handles database operations for the banking system.
    Manages user accounts, authentication, and transactions.
    """

    def __init__(self, name):
        self.name = name
        self.connection = None

    def get_connection(self):
        
        if self.connection is None:
            self.connection = sqlite3.connect(self.name, check_same_thread=False, timeout=10)
        return self.connection
    
    def get_cursor(self):
        return self.get_connection().cursor()
    
    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def create_account(self, acc_id: str, usr_id: str, acc_name: str, acc_balance: float) -> bool:
        """Creates a new account in the database."""

        cursor = self.get_cursor()
        cursor.execute(
            "INSERT INTO Account (accID, accType, usrID, accValue) VALUES (?, ?, ?, ?)",
            (acc_id, acc_name, usr_id, acc_balance)
        )
        self.connection.commit()
        self.close_connection()
        return True

    def create_user(self, usr_id: str, usr_name: str, email: str, password: str, role_id: int) -> bool:
        """Creates a new user in the database."""
        cursor = self.get_cursor()

        cursor.execute(
            "INSERT INTO User (usrID, usrName, email, password, RoleID) VALUES (?, ?, ?, ?, ?)",
            (usr_id, usr_name, email, password, role_id)
        )
        self.connection.commit()
        self.close_connection()
        return True

    def get_user_accounts(self, usr_id: str) -> list[Account]:
        """Retrieves all accounts for a given user ID."""

        cursor = self.get_cursor()

        cursor.execute("SELECT * FROM Account WHERE usrID=?", (usr_id,))
        rows = cursor.fetchall()

        accounts = []
        for row in rows:
            acc_id = row[0]
            acc_value = row[1]
            acc_type = row[2]
            accounts.append(Account(acc_id, acc_type, acc_value))

        self.connection.commit()
        self.close_connection()
        return accounts

    def get_users(self, usr_id: str) -> list[dict]:
        """Retrieves user data by user ID."""

        cursor = self.get_cursor()

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

        self.close_connection()
        return users

    def user_login(self, user_name: str, password: str) -> dict | None:
        """Authenticates a user and returns their data if successful."""

        cursor = self.get_cursor()

        cursor.execute(
            "SELECT * FROM User WHERE usrName=? AND password=?",
            (user_name, password)
        )
        row = cursor.fetchone()

        self.close_connection()

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

        cursor = self.get_cursor()

        cursor.execute("SELECT * FROM Account WHERE accID=?", (random_id,))
        rows = cursor.fetchall()

        self.close_connection()
        return bool(rows)

    def email_in_use(self, email_address: str) -> bool:
        """Returns True if the email address is in use."""

        cursor = self.get_cursor()

        cursor.execute("SELECT * FROM User WHERE email=?", (email_address,))
        rows = cursor.fetchall()

        self.close_connection()
        return bool(rows)

    def user_id_in_use(self, random_id: str) -> bool:
        """Returns True if the user ID is in use."""

        cursor = self.get_cursor()

        cursor.execute("SELECT * FROM User WHERE usrID=?", (random_id,))
        rows = cursor.fetchall()

        self.close_connection()
        return bool(rows)

    def withdraw_from_account(self, account_id: str, amount: float) -> list[str]:
        """Withdraws funds from an account."""

        cursor = self.get_cursor()

        output = []
        cursor.execute("SELECT accValue FROM Account WHERE accID=?", (account_id,))
        result = cursor.fetchone()

        if result:
            value = float(result[0])  # Ensure value is treated as float
        else:
            output.append("Error: Withdrawal Account not found")
            self.close_connection()
            return output

        if value < amount:
            output.append("Error: Insufficient Funds")
        else:
            new_value = value - amount
            cursor.execute("BEGIN TRANSACTION;")
            cursor.execute("UPDATE Account SET accValue=? WHERE accID=?",(new_value, account_id))
            self.connection.commit()

        self.close_connection()
        return output

    def deposit_to_account(self, account_id: str, amount: float) -> list[str]:
        """Deposits funds into an account."""
        if amount <= 0:
            return ["Error: Deposit amount must be greater than zero"]

        cursor = self.get_cursor()

        cursor.execute("SELECT accValue FROM Account WHERE accID=?", (account_id,))
        result = cursor.fetchone()

        if result:
            value = float(result[0])  # Ensure value is treated as float
        else:
            self.close_connection()
            return ["Error: Depositing Account not found"]

        new_value = value + amount
        cursor.execute("BEGIN TRANSACTION;") 
        cursor.execute("UPDATE Account SET accValue=? WHERE accID=?", (new_value, account_id))
        self.connection.commit()

        self.close_connection()
        return []

    def password_reset(self, user_name: str, email: str, password: str) -> bool:
        """Resets a user's password."""

        cursor = self.get_cursor()

        cursor.execute(
            "UPDATE User SET password=? WHERE usrName=? AND email=?",
            (password, user_name, email)
        )
        self.connection.commit()
        self.close_connection()
        return True

    def get_user_by_username(self, username: str) -> dict | None:
        """Retrieves user data by username."""

        cursor = self.get_cursor()

        cursor.execute("SELECT * FROM User WHERE usrName=?", (username,))
        row = cursor.fetchone()

        self.close_connection()

        if row:
            return {
                "usrID": row[0],
                "usrName": row[1],
                "email": row[2],
                "password": row[3],
                "RoleID":row[4]
            }
        return None

    def get_user_by_email(self, email: str) -> dict | None:
        """Retrieves user by email."""

        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM User WHERE email=?", (email,))
        row = cursor.fetchone()
        self.close_connection()

        if row:
            return {
                "usrID": row[0],
                "usrName": row[1],
                "email": row[2],
                "password": row[3],
                "RoleID":row[4]
            }
        return None
    
    def get_user_creation_log(self, identifier:str) -> dict | None:
        "Retireves the log entry by a user's ID"

        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM auditUserCreationLog WHERE usrID=? OR email=? OR usrname=?", 
        (identifier, identifier, identifier)
        )
        rows = cursor.fetchall()
        self.close_connection()

        return [
            {"ID": row[0], "usrID": row[1], "email": row[2], "password": row[3]}
            for row in rows
        ] if rows else []
    
    
    
    def rollback(self) -> bool:
        """Rolls Back Most recent transaction"""

        cursor = self.get_cursor()
        cursor.execute("ROLLBACK;")
        self.close_connection()



    
