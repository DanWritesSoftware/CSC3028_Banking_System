"""
user_management.py
Handles user authentication, registration, password management, and 2FA.
"""

import logging
import random
import sqlite3
import time
import smtplib
import socket
import hashlib
from email.message import EmailMessage
from typing import Optional, Dict
from Account import Account
from flask import session

from encryption_utils import encrypt_string_with_file_key

import bcrypt
from database_handler import Database
from input_validator import InputValidator

from encryption_utils import encrypt_string_with_file_key
from encryption_utils import decrypt_string_with_file_key

import os 

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Database and validation instances
db_manager = Database("BankingData.db")
input_validator = InputValidator()

# Constants
USER_ID_LENGTH = 10
CODE_EXPIRATION = 600  # 10 minutes in seconds
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_FROM = "csc3028.evil.banking.system"
# EMAIL PASSWORD STORED IN TXT FILE - SEE get_gmail_password

class UserManager:
    """Handles user authentication, registration, and 2FA."""

    _verification_codes = {}

    def __init__(self) -> None:
        pass

    def create_account(self, user_id: str) -> dict:
        """Creates a new bank account with 10-digit number."""
        account_number = ''.join(random.choices('0123456789', k=10))
        if db_manager.create_account(
                acc_id=account_number,  # First parameter matches database method
                usr_id=user_id,  # Second parameter
                acc_name="Primary Checking",  # Default account name
                acc_balance=0.0  # Default starting balance
        ):
            return {"account_number": account_number}
        return {}

    def sign_up_customer(self, username: str, email: str, password: str, confirm_password: str) -> str:
        """Registers a new user with hashed password security."""
        if not input_validator.validate_username(username):
            logging.warning("Invalid username provided.")
            return "Invalid username, please try again."
        if not input_validator.validate_email(email):
            logging.warning("Invalid email format.")
            return "Invalid email, please try again."
        if not input_validator.validate_password_complexity(password):
            logging.warning("Password does not meet complexity requirements.")
            return "Password not complex enough, please try again."
        if password != confirm_password:
            return "Passwords do not match."
        if db_manager.email_in_use(email):
            return "Email address already in use!"

        while True:
            user_id = ''.join(random.choices('0123456789', k=USER_ID_LENGTH))
            if not db_manager.user_id_in_use(user_id):
                break

        username_hash = hashlib.sha256(username.lower().encode()).hexdigest()

        email_hash = hashlib.sha256(email.lower().encode()).hexdigest()

        encrypted_username = encrypt_string_with_file_key(username)

        encrypted_email = encrypt_string_with_file_key(email)

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        db_manager.create_user(user_id, encrypted_username, encrypted_email, hashed_password, 3, username_hash, email_hash)
        logging.info("User %s registered successfully with ID %s.", username, user_id)
        return user_id

    def sign_up_teller(self, username: str, email: str, password: str, confirm_password: str) -> str:
        """Registers a new user with hashed password security."""
        if not input_validator.validate_username(username):
            logging.warning("Invalid username provided.")
            return "Invalid username, please try again."
        if not input_validator.validate_email(email):
            logging.warning("Invalid email format.")
            return "Invalid email, please try again."
        if not input_validator.validate_password_complexity(password):
            logging.warning("Password does not meet complexity requirements.")
            return "Password not complex enough, please try again."
        if password != confirm_password:
            return "Passwords do not match."
        if db_manager.email_in_use(email):
            return "Email address already in use!"

        while True:
            user_id = ''.join(random.choices('0123456789', k=USER_ID_LENGTH))
            if not db_manager.user_id_in_use(user_id):
                break

        username_hash = hashlib.sha256(username.lower().encode()).hexdigest()

        email_hash = hashlib.sha256(email.lower().encode()).hexdigest()

        encrypted_username = encrypt_string_with_file_key(username)

        encrypted_email = encrypt_string_with_file_key(email)

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        db_manager.create_user(user_id, encrypted_username, encrypted_email, hashed_password, 2, username_hash, email_hash)
        logging.info("User %s registered successfully.", username)
        return "Teller registered successfully!"

    def sign_up_admin(self, username: str, email: str, password: str, confirm_password: str) -> str:
        """Registers a new user with hashed password security."""
        if not input_validator.validate_username(username):
            logging.warning("Invalid username provided.")
            return "Invalid username, please try again."
        if not input_validator.validate_email(email):
            logging.warning("Invalid email format.")
            return "Invalid email, please try again."
        if not input_validator.validate_password_complexity(password):
            logging.warning("Password does not meet complexity requirements.")
            return "Password not complex enough, please try again."
        if password != confirm_password:
            return "Passwords do not match."
        if db_manager.email_in_use(email):
            return "Email address already in use!"

        while True:
            user_id = ''.join(random.choices('0123456789', k=USER_ID_LENGTH))
            if not db_manager.user_id_in_use(user_id):
                break

        username_hash = hashlib.sha256(username.lower().encode()).hexdigest()

        email_hash = hashlib.sha256(email.lower().encode()).hexdigest()

        encrypted_username = encrypt_string_with_file_key(username)

        encrypted_email = encrypt_string_with_file_key(email)

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        db_manager.create_user(user_id, encrypted_username, encrypted_email, hashed_password, 1, username_hash, email_hash)
        logging.info("User %s registered successfully.", username)
        return "Teller registered successfully!"


    def login(self, username: str, password: str) -> Optional[Dict]:
        """Initiates authentication and triggers 2FA email."""
        try:
            user_data = db_manager.get_user_encrypted_search(username)
            if not user_data:
                logging.warning("Login failed: User not found.")
                
                return None

            stored_hash = user_data['password']
            if bcrypt.checkpw(password.encode(), stored_hash.encode()):
                encrypted_email = user_data['email']

                try:
                    decrypted_email = decrypt_string_with_file_key(encrypted_email)

                except Exception as e:
                    logging.error(f"Failed to decrypt email for 2FA: {e}")
                    return None
        
                code = self._generate_verification_code(decrypted_email)
                self._send_verification_email(decrypted_email, code)

                return {'requires_2fa': True, 'email': decrypted_email}

            logging.warning("Incorrect password.")
            return None
        except sqlite3.Error as e:
            logging.error("Database error during login: %s", e)
            return None

    def verify_2fa(self, email: str, code: str) -> Optional[Dict]:
        """Validates 2FA code."""
        stored_data = self._verification_codes.get(email)

        if not stored_data:
            logging.warning("No verification attempt for %s", email)
            return None

        if time.time() > stored_data['expires']:
            logging.warning("Expired code for %s", email)
            del self._verification_codes[email]
            return None

        if stored_data['code'] == code:
            del self._verification_codes[email]

            user_data = db_manager.get_user_by_email(email)
            if not user_data:
                logging.error("User not found during 2FA verification for %s", email)
                return None
            
            try:
                session['username'] = decrypt_string_with_file_key(user_data['usrName'])

            except Exception as e:
                logging.error("Failed to decrypt username for the session: %s", e)
                return None
            
            session['user_id'] = user_data['usrID']
            session['email'] = user_data['email']
            session['role_id'] = user_data['RoleID']

            logging.info("2FA success. User %s authenticated", session['username'])
            return user_data
    
        else:
            logging.warning("Invalid code for %s", email)
            return None

    def _generate_verification_code(self, email: str) -> str:
        """Generates 6-digit verification code."""
        code = ''.join(random.choices('0123456789', k=6))
        self._verification_codes[email] = {
            'code': code,
            'expires': time.time() + CODE_EXPIRATION
        }

        env = os.getenv("FLASK_ENV", "").lower()

        if env in ["testing, development"]:
            print(f"[DEV MODE] 2FA code for {email}: {code}")
            logging.debug(f"[DEV MODE] 2FA code for {email}: {code}")
        return code

    def _send_verification_email(self, email: str, code: str) -> None:
        """Sends verification email via SMTP."""
        msg = EmailMessage()
        msg.set_content(f"Your verification code: {code}\nCode valid for 10 minutes.")
        msg['Subject'] = 'Your Banking App Verification Code'
        msg['From'] = EMAIL_FROM
        msg['To'] = email

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=60) as server:
                server.starttls()
                server.login(EMAIL_FROM, self.get_gmail_password())
                server.send_message(msg)
            logging.info("Verification email sent to %s", email)
        except smtplib.SMTPException as e:
            logging.error("SMTP error occurred: %s", str(e))
        except socket.error as se:
            logging.error("Socket error occurred: %s", str(se))
        except OSError as oe:
            logging.error("OS error occurred: %s", str(oe))
        except Exception as ex:
            logging.error("Unexpected error occurred: %s", str(ex))

    def password_reset(self, username: str, email: str,
                     new_password: str, confirm_password: str) -> str:
        """Handles password reset."""
        if new_password != confirm_password:
            return "Passwords do not match."

        if not input_validator.validate_password_complexity(new_password):
            return "Password not secure."

        # Check if user exists
        user_data = db_manager.get_user_by_username(username)
        if not user_data:
            return "User does not exist."

        if user_data['email'] != email:
            return "Email does not match our records."

        hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        try:
            if db_manager.password_reset(username, email, hashed_password):
                logging.info("Password reset for %s", username)
                return "Password reset successfully."
            return "Password reset failed."
        except sqlite3.Error as e:
            return f"Database error: {e}"

    def get_database(self):
        return db_manager

    def get_user_account_info_from_index(self, user_id: str, index: int) -> Account:
        logging.info(f"Attempting to retrieve account at index {index} for user_id={user_id}")
        user_accounts = db_manager.get_user_accounts(user_id)
        try:
            output = user_accounts[index]
            logging.info(f"Retrieved account: Number={output.accountNumber}, Type={output.type}, Balance={output.balance}")
        except IndexError:
            logging.error(f"Index {index} out of bounds for user {user_id}. Total accounts: {len(user_accounts)}")
            raise
        except Exception as e:
            logging.exception(f"Unexpected error retrieving account at index {index} for user {user_id}: {str(e)}")
            raise

        return output

    def transfer_funds_by_account_number(self, user_id: str, from_account_id: str, to_account_id: str, amount: float) -> list[str]:
        """
        Transfers funds from a user's account (by account number) to another account (also by account number).
        Returns a list of error messages, or an empty list on success.
        """
        if amount <= 0:
            return ["Error: Transfer amount must be greater than zero."]

        try:
            user_accounts = db_manager.get_user_accounts(user_id)

            # Find the source account object by account number
            from_account = None
            for account in user_accounts:
                if str(account.accountNumber) == str(from_account_id):
                    from_account = account
                    break

            if from_account is None:
                return ["Error: Source account not found."]

            # Prevent self-transfer
            if str(from_account.accountNumber) == str(to_account_id):
                return ["Error: Cannot transfer to the same account."]

            # Withdraw from source account
            withdraw_result = db_manager.withdraw_from_account(from_account.accountNumber, amount)
            if withdraw_result:
                return withdraw_result  # Withdrawal failed

            # Deposit into destination account
            deposit_result = db_manager.deposit_to_account(to_account_id, amount)
            if deposit_result:
                # Rollback the withdrawal
                db_manager.deposit_to_account(from_account.accountNumber, amount)
                return deposit_result

            return []  # Success

        except Exception as e:
            logging.exception(f"Exception during transfer: {str(e)}")
            return [f"Unexpected error during transfer: {str(e)}"]

    def get_gmail_password(self) -> str:
        """Get gmail password from text file in directory"""
        filepath = "gmail_password.txt"
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return file.readline().strip()
        except FileNotFoundError:
            print(f"PLEASE ENTER GMAIL APP PASSWORD IN {filepath}. IF IT DOESN'T EXIST, CREATE IT.")
            return ""
        except Exception as e:
            print(f"Error reading file: {e}")
            return ""