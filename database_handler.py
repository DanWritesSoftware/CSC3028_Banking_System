"""
database_handler.py
This module handles database operations for the banking system.
"""

import sqlite3
import threading
import hashlib
import traceback
import shutil
import os
import secrets
from Account import Account
from audit_log import AuditLog
from encryption_utils import decrypt_string_with_file_key, encrypt_string_with_file_key
from signature_utils import sign_message
from datetime import datetime
from cryptography.fernet import Fernet

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
            encrypted_acc_balance = encrypt_string_with_file_key(str(acc_balance))

            encrypted_acc_type = encrypt_string_with_file_key(acc_name)

            conn.execute(
                "INSERT INTO Account (accID, accType, usrID, accValue) VALUES (?, ?, ?, ?)",
                (acc_id, encrypted_acc_type, usr_id, encrypted_acc_balance)
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
        accounts = []
        for row in cursor.fetchall():
            try:
                decrypted_type = decrypt_string_with_file_key(row[1])

                if isinstance(row[3], (int, float)):
                    decrypted_balance = float(row[3])
                else:
                    decrypted_balance = float(decrypt_string_with_file_key(row[3]))

                accounts.append(Account(row[0], decrypted_type, decrypted_balance))

            except Exception as e:
                print(f"[ERROR] Decryption Failed for account {row[0]}:{e}")
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

                # Encrypted Audit with digital signature
                operation = "WITHDRAW"
                table_name = "Account"
                timestamp = datetime.utcnow().isoformat()
                old_value = encrypt_string_with_file_key(f"Balance: {balance}")
                new_value = encrypt_string_with_file_key(f"Balance: {new_balance}")
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
                old_value = encrypt_string_with_file_key(f"Balance: {balance}")
                new_value = encrypt_string_with_file_key(f"Balance: {new_balance}")
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
                cursor.execute("SELECT accValue FROM Account WHERE accID=?", (from_account_id,))
                from_result = cursor.fetchone()
                if not from_result:
                    return ["Error: Source Account Not Found"]
                from_balance = float(decrypt_string_with_file_key(from_result[0]))

                if from_balance < amount:
                    return ["Error: Insufficient Funds, Brokie."]
                
                cursor.execute("SELECT accValue FROM Account WHERE accID=?", (to_account_id,))

                to_result = cursor.fetchone()

                if not to_result:
                    return ["Error: Destination Account Not Found"]
                
                to_balance = float(decrypt_string_with_file_key(to_result[0]))

                new_from_balance = from_balance - amount
                new_to_balance = to_balance + amount

                encrypted_from_balance = encrypt_string_with_file_key(str(new_from_balance))
                encrypted_to_balance = encrypt_string_with_file_key(str(new_to_balance))

                #Update Both Accounts
                cursor.execute("UPDATE Account SET accValue = ? WHERE accID = ?",
                               (encrypted_from_balance, from_account_id))
                cursor.execute("UPDATE Account SET accValue = ? WHERE accID = ?",
                               (encrypted_to_balance, to_account_id))
                timestamp = datetime.utcnow().isoformat()

                withdraw_old_value = encrypt_string_with_file_key(f"Balance: {from_balance}")
                withdraw_new_value = encrypt_string_with_file_key(f"Balance: {new_from_balance}")
                deposit_old_value = encrypt_string_with_file_key(f"Balance: {to_balance}")
                deposit_new_value = encrypt_string_with_file_key(f"Balance: {new_to_balance}")

                withdraw_message = f"TRANSFER-WITHDRAWAL|Account|Balance: {from_balance}|Balance: {new_from_balance}|{timestamp}"
                deposit_message = f"TRANSFER-DEPOSIT|Account|Balance: {to_balance}|Balance: {new_to_balance}|{timestamp}"
                withdraw_signature = sign_message(withdraw_message).hex()
                deposit_signature = sign_message(deposit_message).hex()

                cursor.execute(
                "INSERT INTO auditLog (Operation, TableName, oldValue, newValue, ChangedAt, signature) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                ("TRANSFER-WITHDRAWAL", "Account", withdraw_old_value, withdraw_new_value, timestamp, withdraw_signature)
            )

            cursor.execute(
                "INSERT INTO auditLog (Operation, TableName, oldValue, newValue, ChangedAt, signature) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                ("TRANSFER-DEPOSIT", "Account", deposit_old_value, deposit_new_value, timestamp, deposit_signature)
            )

            conn.commit()
                
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

    def secure_delete_user(self, usr_id: str) -> bool:
        """
        Securely deletes a user by overwriting sensitive fields and removing their record.

        Args:
            usr_id (str): The ID of the user to delete.

            Returns:
                bool: True if successful, False otherwise.
        """

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Fetch Original user Data
            cursor.execute("SELECT usrName, email, password FROM User WHERE usrID=?", (usr_id,))
            original = cursor.fetchone()

            if not original:
                print (f"[WARN] User {usr_id} not found.")
                return False
            
            try:
                original_usr_name = decrypt_string_with_file_key(original[0])
                original_email = decrypt_string_with_file_key(original[1])
            except Exception as decryption_error:
                print(f"[ERROR] Failed to decrypt fields for user {usr_id}: {decryption_error}")
                return False
            original_password = original[2]

            fake_name = encrypt_string_with_file_key(secrets.token_hex(8))
            fake_email = encrypt_string_with_file_key(secrets.token_hex(8) + "@Deleted.local")
            fake_password = secrets.token_hex(32)
            fake_hash = hashlib.sha256(secrets.token_bytes(32)).hexdigest()

            cursor.execute("UPDATE User SET usrName=?, email=?, password=?, usrNameHash=?, emailHash=? WHERE usrID=?",
                           (fake_name, fake_email, fake_password, fake_hash, fake_hash, usr_id))
            
            operation = "DELETE-USER"
            table_name = "User"
            time_stamp = datetime.utcnow().isoformat()
            old_value = encrypt_string_with_file_key(f"usrID: {usr_id}, userName: {original_usr_name}, email: {original_email}, password: {original_password}")

            new_value = encrypt_string_with_file_key("Record Deleted")

            message = f"{operation}|{table_name}|{old_value}|{new_value}|{time_stamp}"

            signature = sign_message(message).hex()

            cursor.execute("INSERT INTO auditLog (Operation, TableName, oldValue, newValue, ChangedAt, signature) VALUES (?, ?, ?, ?, ?, ?)", (operation, table_name, old_value, new_value, time_stamp, signature))

            cursor.execute("DELETE FROM User WHERE usrID=?", (usr_id,))

            conn.commit()

            self.get_connection().execute("VACUUM")

            print(f"[INFO] Securely deleted user {usr_id}")

            return True
        
        except Exception as e:
            print(f"[ERROR] Deletion failed for user: {usr_id}: {e}")

            return False
        
    def secure_delete_account(self, acc_id: str) -> bool:
        """
        Securely deletes an account by overwriting sensitive fields and removing the record.

        Args:
            acc_id (str): The ID of the account to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Fetch original account information
            cursor.execute("SELECT accType, accValue FROM Account WHERE accID=?", (acc_id,))
            original = cursor.fetchone()

            if not original:
                print(f"[WARN] Account {acc_id} not found.")
                return False
            
            try:
                original_type = decrypt_string_with_file_key(original[0])
                original_value = decrypt_string_with_file_key(original[1])
            except Exception as decryption_error:
                print(f"[ERROR] Failed to decrypt account {acc_id} data: {decryption_error}")
                return False

            fake_type = encrypt_string_with_file_key("CLOSED_" + secrets.token_hex(4))
            fake_value = encrypt_string_with_file_key("0.00")

            cursor.execute("UPDATE Account SET accType=?, accValue=? WHERE accID=?", (fake_type, fake_value, acc_id))

            # Prepare Audit Log
            operation = "DELETE-ACCOUNT"
            table_name = "Account"
            time_stamp = datetime.utcnow().isoformat()
            old_value = encrypt_string_with_file_key(f"accID: {acc_id}, Type: {original_type}, Value: {original_value}")
            new_value = encrypt_string_with_file_key("Record Deleted")

            message = f"{operation}|{table_name}|{old_value}|{new_value}|{time_stamp}"
            signature = sign_message(message).hex()

            cursor.execute("INSERT INTO auditLog (Operation, TableName, oldValue, newValue, ChangedAt, signature) VALUES (?, ?, ?, ?, ?, ?)", 
                           (operation, table_name, old_value, new_value, time_stamp, signature))
            
            # Delete the account record
            cursor.execute("DELETE FROM Account WHERE accID=?", (acc_id,))
            conn.commit()

            self.get_connection().execute("VACUUM")

            print(f"[INFO] Securely Deleted Account: {acc_id}")

            return True
        except Exception as e:
            print(f"[ERROR] Failed to delete Account: {acc_id}: {e}")

            return False

    def __del__(self):
        """Clean up connections when instance is destroyed"""
        if hasattr(self.local, 'conn') and self.local.conn:
            self.local.conn.close()

    def backup_encrypted_database(self, backup_path: str, encryption_key_path: str) -> bool:
        """
        Creates an encrypted backup using VACUUM INTO.
        Ensures the backup includes all schema and data safely.
        """
        try:
            # Create temp clean DB file with VACUUM INTO
            temp_clean_path = backup_path + ".tmp_clean"

            conn = self.get_connection()
            conn.execute(f"VACUUM INTO '{temp_clean_path}'")
            conn.commit()

            # Load encryption key
            with open(encryption_key_path, 'rb') as key_file:
                key = key_file.read()
            cipher = Fernet(key)

            # Read flushed db into bytes
            with open(temp_clean_path, 'rb') as f:
                db_data = f.read()

            # Encrypt and save
            encrypted = cipher.encrypt(db_data)
            with open(backup_path, 'wb') as f:
                f.write(encrypted)

            os.remove(temp_clean_path)
            return True

        except Exception as e:
            print(f"[ERROR] Encrypted backup failed: {e}")
            return False

    def restore_encrypted_backup(self, backup_path: str, encryption_key_path: str) -> bool:
        """
        Restores the encrypted database backup by decrypting and replacing the current DB file.
        
        Args:
            backup_path (str): Path to the encrypted backup file.
            encryption_key_path (str): Path to the Fernet key used for decryption.
        
        Returns:
            bool: True if restore is successful, False otherwise.
        """
        try:
            # Load the encryption key
            with open(encryption_key_path, 'rb') as key_file:
                key = key_file.read()
            cipher = Fernet(key)

            # Read and decrypt the backup data
            with open(backup_path, 'rb') as encrypted_file:
                encrypted_data = encrypted_file.read()
            decrypted_data = cipher.decrypt(encrypted_data)

            # Write the decrypted data back to the live database file
            self.close_all_connections()
            with open(self.name, 'wb') as db_file:
                db_file.write(decrypted_data)

            print(f"[INFO] Database successfully restored from: {backup_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to restore encrypted backup: {e}")
            return False
