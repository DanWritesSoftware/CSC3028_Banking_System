"""
database_handler.py
This module handles database operations for the banking system.
"""

import sqlite3
import threading
import hashlib
from Account import Account
from audit_log import AuditLog
from encryption_utils import decrypt_string_with_file_key
from signature_utils import sign_message
from datetime import datetime

class Database:
    """
    Handles database operations with thread-local connection pooling.
    """

    def __init__(self, name):
        self.name = name
        self.local = threading.local()

    def get_connection(self):
        """Get or create a thread-local connection"""
        if not hasattr(self.local, 'conn') or self.local.conn is None:
            self.local.conn = sqlite3.connect(
                self.name,
                check_same_thread=False,
                timeout=10
            )
            self.local.conn.execute("PRAGMA journal_mode=WAL")
        return self.local.conn
    
    def get_cursor(self):
        return self.get_connection().cursor()

    def create_account(self, acc_id: str, usr_id: str, acc_name: str, acc_balance: float) -> bool:
        conn = self.get_connection()
        try:
            conn.execute(
                "INSERT INTO Account (accID, accType, usrID, accValue) VALUES (?, ?, ?, ?)",
                (acc_id, acc_name, usr_id, acc_balance)
            )
            conn.commit()
            return True
        except sqlite3.Error as e:
            conn.rollback()
            raise e

    def create_user(self, usr_id: str, usr_name: str, email: str, password: str, role_id: int, username_hash: str, email_hash: str) -> bool:
        conn = self.get_connection()
        try:

            conn.execute(
                "INSERT INTO User (usrID, usrName, email, password, RoleID, usrNameHash, emailHash) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (usr_id, usr_name, email, password, role_id, username_hash, email_hash)
            )
            conn.commit()
            return True
        except sqlite3.Error as e:
            conn.rollback()
            raise e

    def get_user_accounts(self, usr_id: str) -> list[Account]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Account WHERE usrID=?", (usr_id,))
        accounts = [
            Account(row[0], row[2], float(row[1])) 
            for row in cursor.fetchall()
        ]
        return accounts

    def get_users(self, usr_id: str) -> list[dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE usrID=?", (usr_id,))
        return [{
            "usrID": row[0],
            "usrName": row[1],
            "email": row[2],
            "password": row[3]
        } for row in cursor.fetchall()]

    def user_login(self, user_name: str, password: str) -> dict | None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM User WHERE usrName=? AND password=?",
            (user_name, password)
        )
        row = cursor.fetchone()
        return {
            "usrID": row[0],
            "usrName": row[1],
            "email": row[2],
            "password": row[3]
        } if row else None

    def account_id_in_use(self, random_id: str) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM Account WHERE accID=?", (random_id,))
        return bool(cursor.fetchone())

    def email_in_use(self, email_address: str) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM User WHERE email=?", (email_address,))
        return bool(cursor.fetchone())

    def user_id_in_use(self, random_id: str) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM User WHERE usrID=?", (random_id,))
        return bool(cursor.fetchone())

    def withdraw_from_account(self, account_id: str, amount: float) -> list[str]:
        conn = self.get_connection()
        errors = []
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("SELECT accValue FROM Account WHERE accID=?", (account_id,))
                result = cursor.fetchone()
                
                if not result:
                    errors.append("Error: Account not found")
                    return errors
                
                balance = float(result[0])
                if balance < amount:
                    errors.append("Error: Insufficient funds")
                    return errors
                
                new_balance = balance - amount
                cursor.execute(
                    "UPDATE Account SET accValue=? WHERE accID=?",
                    (new_balance, account_id)
                )

                # Audit with digital signature
                operation = "WITHDRAW"
                table_name = "Account"
                timestamp = datetime.utcnow().isoformat()
                old_value = f"Balance: {balance}"
                new_value = f"Balance: {new_balance}"
                message = f"{operation}|{table_name}|{old_value}|{new_value}|{timestamp}"
                signature = sign_message(message).hex()

                cursor.execute(
                    "INSERT INTO auditLog (Operation, TableName, oldValue, newValue, ChangedAt, signature) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (operation, table_name, old_value, new_value, timestamp, signature)
                )

            return []
        except sqlite3.Error as e:
            errors.append(f"Database error: {str(e)}")
            return errors

    def deposit_to_account(self, account_id: str, amount: float) -> list[str]:
        if amount <= 0:
            return ["Error: Invalid deposit amount"]
        
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("SELECT accValue FROM Account WHERE accID=?", (account_id,))
                
                result = cursor.fetchone()

                if not result:
                    return ["Error: Account not found"]
                
                balance = float(result[0])
                new_balance = balance + amount

                cursor.execute ("UPDATE Account SET accValue = ? WHERE accID = ?", (new_balance, account_id))
                
                # Audit with digital signature
                operation = "DEPOSIT"
                table_name = "Account"
                timestamp = datetime.utcnow().isoformat()
                old_value = f"Balance: {balance}"
                new_value = f"Balance: {new_balance}"
                message = f"{operation}|{table_name}|{old_value}|{new_value}|{timestamp}"
                signature = sign_message(message).hex()

                cursor.execute(
                    "INSERT INTO auditLog (Operation, TableName, oldValue, newValue, ChangedAt, signature) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (operation, table_name, old_value, new_value, timestamp, signature)
                )
            return []
        except sqlite3.Error as e:
            return [f"Database error: {str(e)}"]

    def transfer_funds_by_account_number(self, from_account_id: str, to_account_id: str, amount: float) -> list[str]:
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                # Check source account
                cursor.execute(
                    "SELECT accValue FROM Account WHERE accID=?",
                    (from_account_id,)
                )
                from_result = cursor.fetchone()
                if not from_result:
                    return ["Error: Source Account Not Found"]
                from_balance = float(from_result[0])

                if from_balance < amount:
                    return ["Error: Insufficient Funds"]
                
                cursor.execute("SELECT accValue FROM Account WHERE accID=?", (to_account_id,))

                to_result = cursor.fetchone()

                if not to_result:
                    return ["Error: Destination Account Not Found"]
                
                to_balance = float(to_result[0])

                new_from_balance = from_balance - amount
                
                new_to_balance = to_balance + amount

                cursor.execute(
                    "UPDATE Account SET accValue = ? WHERE accID = ?", 
                    (new_from_balance, from_account_id)
                )

                cursor.execute(
                    "UPDATE Account SET accValue = ? WHERE accID = ?",
                    (new_to_balance, to_account_id)
                )

                timestamp = datetime.utcnow().isoformat()

                # Log withdrawal audit
                withdraw_message = f"TRANSFER-WITHDRAWAL|Account|Balance: {from_balance}|Balance: {new_from_balance}|{timestamp}"
                withdraw_signature = sign_message(withdraw_message).hex()
                cursor.execute(
                    "INSERT INTO auditLog (Operation, TableName, oldValue, newValue, ChangedAt, signature) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    ("TRANSFER-WITHDRAWAL", "Account", f"Balance: {from_balance}", f"Balance: {new_from_balance}", timestamp, withdraw_signature)
                )

                # Log deposit audit
                deposit_message = f"TRANSFER-DEPOSIT|Account|Balance: {to_balance}|Balance: {new_to_balance}|{timestamp}"
                deposit_signature = sign_message(deposit_message).hex()
                cursor.execute(
                    "INSERT INTO auditLog (Operation, TableName, oldValue, newValue, ChangedAt, signature) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    ("TRANSFER-DEPOSIT", "Account", f"Balance: {to_balance}", f"Balance: {new_to_balance}", timestamp, deposit_signature)
                )
                
            return []
        except sqlite3.Error as e:
            return [f"Database error: {str(e)}"]

    def password_reset(self, user_name: str, email: str, password: str) -> bool:
        conn = self.get_connection()
        try:
            with conn:
                conn.execute(
                    "UPDATE User SET password=? WHERE usrName=? AND email=?",
                    (password, user_name, email)
                )
            return True
        except sqlite3.Error:
            return False

    def get_user_by_username(self, username: str) -> dict | None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User")
        rows = cursor.fetchall()

        for row in rows:
            try:
                decrypted_username = decrypt_string_with_file_key(row[1])
                if decrypted_username == username:
                    return {
                        "usrID": row[0],
                        "usrName": row[1],
                        "email": row[2],
                        "password": row[3],
                        "RoleID": row[4]
                    }
            except Exception as e:
                continue
        return None
    
    def get_user_encrypted_search(self, username: str) -> dict | None:
        conn = self.get_connection()
        cursor = conn.cursor()
        username_hash = hashlib.sha256(username.lower().encode()).hexdigest()

        cursor.execute("SELECT* FROM User WHERE usrNameHash = ?", (username_hash,))

        row = cursor.fetchone()

        if row:
            return {
                "usrID": row[0],
                "usrName": row[1],
                "email": row[2],
                "password": row[3],
                "RoleID": row[4]
            }
        return None

    def get_user_by_email(self, email: str) -> dict | None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        rows = cursor.fetchall()

        for row in rows:
            try:
                decrypted_email = decrypt_string_with_file_key(row[2])
                if decrypted_email == email:        
                    return {
                        "usrID": row[0],
                        "usrName": row[1],
                        "email": row[2],
                        "password": row[3],
                        "RoleID": row[4]
                    } if row else None
            except Exception:
                continue

        return None
    
    def get_user_encrypted_email_search(self, email: str) -> dict | None:
        conn = self.get_connection()
        cursor = conn.cursor()
        email_hash = hashlib.sha256(email.lower().encode()).hexdigest()

        cursor.execute("SELECT* FROM User WHERE emailHash = ?", (email_hash,))

        row = cursor.fetchone()

        if row:
            return {
                "usrID": row[0],
                "usrName": row[1],
                "email": row[2],
                "password": row[3],
                "RoleID": row[4]
            }
        return None

    def get_user_creation_log(self, identifier: str) -> list:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM auditUserCreationLog WHERE usrID=? OR email=? OR usrname=?",
            (identifier, identifier, identifier)
        )
        return [
            {"ID": row[0], "usrID": row[1], "email": row[2], "password": row[3]}
            for row in cursor.fetchall()
        ]

    def rollback(self) -> bool:
        conn = self.get_connection()
        try:
            conn.rollback()
            return True
        except sqlite3.Error:
            return False

    def get_audit_logs(self) -> list:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM auditLog")
        return [
            AuditLog(
                row[0],  # ID
                row[1],  # Operation
                row[2],  # TableName
                row[3],  # oldValue
                row[4],  # newValue
                row[5],  # ChangedAt
                row[6]   # signature
            ) for row in cursor.fetchall()
        ]

    def close_all_connections(self):
        """Cleanup method for test environment"""
        if hasattr(self.local, 'conn') and self.local.conn:
            self.local.conn.close()
            self.local.conn = None

    def __del__(self):
        """Clean up connections when instance is destroyed"""
        if hasattr(self.local, 'conn') and self.local.conn:
            self.local.conn.close()