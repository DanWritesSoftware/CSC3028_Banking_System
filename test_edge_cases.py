"""
Edge case validation for banking transactions.
Tests extreme values and unexpected inputs.
"""

import unittest
import sqlite3
import os
import hashlib
from database_handler import Database
from deposit_handler import Deposit
from withdrawal_handler import Withdrawal
from encryption_utils import encrypt_string_with_file_key, decrypt_string_with_file_key

class TestEdgeCases(unittest.TestCase):
    """Test cases for extreme values and malicious inputs"""
    
    @classmethod
    def setUpClass(cls):
        """Create dedicated test database with proper schema"""
        print("\n=== Initializing Edge Case Test Database ===")
        cls.db_name = "test_edge_cases.db"
        if os.path.exists(cls.db_name):
            os.remove(cls.db_name)
            
        # Create tables using production schema with updated column names
        with sqlite3.connect(cls.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE User (
                    usrID TEXT PRIMARY KEY,
                    usrName TEXT NOT NULL,
                    email TEXT NOT NULL,
                    password TEXT NOT NULL,
                    RoleID INTEGER,
                    usrNameHash TEXT,
                    emailHash TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE Account (
                    accID TEXT PRIMARY KEY,
                    accValue TEXT NOT NULL,
                    accType TEXT NOT NULL,
                    usrID TEXT,
                    FOREIGN KEY (usrID) REFERENCES User(usrID)
                )
            """)
            cursor.execute("""
                CREATE TABLE auditLog (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Operation TEXT,
                    TableName TEXT,
                    oldValue TEXT,
                    newValue TEXT,
                    ChangedAt TEXT,
                    signature TEXT
                )
            """)
            conn.commit()
        print("Database schema created successfully")

    def setUp(self):
        """Initialize fresh test data for each test"""
        print(f"\n--- Initializing Test: {self._testMethodName} ---")
        self.db = Database(self.db_name)
        
        # Clear previous test data
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("DELETE FROM Account")
            conn.execute("DELETE FROM User")
            conn.commit()

        # Create test user with hashing and encryption
        self.valid_account = "1234567890"
        self.user_id = "edge123"
        self.username = "edgeuser"
        self.email = "edge@test.com"
        
        # Generate hashes for username and email
        username_hash = hashlib.sha256(self.username.lower().encode()).hexdigest()
        email_hash = hashlib.sha256(self.email.lower().encode()).hexdigest()

        # Encrypt username and email
        encrypted_username = encrypt_string_with_file_key(self.username)
        encrypted_email = encrypt_string_with_file_key(self.email)
        
        print(f"Creating test user '{self.username}' with account {self.valid_account} ($100.00)")
        
        # Insert user with all required fields
        with sqlite3.connect(self.db_name) as conn:
            conn.execute(
                "INSERT INTO User (usrID, usrName, email, password, RoleID, usrNameHash, emailHash) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (self.user_id, encrypted_username, encrypted_email, "EdgePass123!", 3, username_hash, email_hash)
            )
        
        # Create account using Database handler (handles encryption)
        self.db.create_account(
            acc_id=self.valid_account,
            usr_id=self.user_id,
            acc_name="Checking",
            acc_balance=100.0
        )

    def get_account_balance(self, account_id: str) -> float:
        """Get balance from database with proper decryption"""
        accounts = self.db.get_user_accounts(self.user_id)
        for account in accounts:
            if account.accountNumber == account_id:
                return account.balance
        return 0.0

    def test_max_transaction_limit(self):
        """Test withdrawal of entire balance"""
        print("\n[Maximum Withdrawal Test]")
        print("Starting balance: $100.00")
        print("Attempting to withdraw $100.00...")
        
        withdrawal = Withdrawal(self.valid_account, 100.0, self.db)
        errors = withdrawal.try_withdrawal()
        
        self.assertEqual(errors, [], "Withdrawal should succeed")
        print("Withdrawal successful with no errors")
        
        balance = self.get_account_balance(self.valid_account)
        print(f"New balance: ${balance:.2f}")
        self.assertEqual(balance, 0.0, "Balance should be zero")
        print("Balance verification passed")

    def test_min_transaction_amount(self):
        """Test smallest possible transaction"""
        print("\n[Minimum Withdrawal Test]")
        print("Starting balance: $100.00")
        print("Attempting to withdraw $0.01...")
        
        withdrawal = Withdrawal(self.valid_account, 0.01, self.db)
        errors = withdrawal.try_withdrawal()
        
        self.assertEqual(errors, [], "Withdrawal should succeed")
        print("Withdrawal successful with no errors")
        
        balance = self.get_account_balance(self.valid_account)
        print(f"New balance: ${balance:.2f}")
        self.assertAlmostEqual(balance, 99.99, places=2, msg="Balance should be $99.99")
        print("Balance verification passed")

    def test_invalid_account_format(self):
        """Test non-numeric account number"""
        print("\n[Invalid Account Format Test]")
        print("Attempting deposit to '12345A7890'...")
        
        deposit = Deposit("12345A7890", 100.0, self.db)
        errors = deposit.try_deposit()
        
        print(f"Received errors: {errors}")
        self.assertIn("Invalid account number", errors, "Should detect invalid account format")
        print("Invalid account format detected successfully")

    def test_sql_injection_attempt(self):
        """Test malicious SQL injection"""
        print("\n[SQL Injection Test]")
        malicious_account = "1234567890'; DROP TABLE Account;--"
        print(f"Attempting deposit to malicious account: {malicious_account}")
        
        deposit = Deposit(malicious_account, 100.0, self.db)
        errors = deposit.try_deposit()
        
        print(f"Received errors: {errors}")
        self.assertIn("Invalid account number", errors, "Should block invalid account before DB operation")
        print("Malicious input blocked successfully")
        
        # Verify database integrity
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Account'")
            result = cursor.fetchone()
            self.assertIsNotNone(result, "Account table should still exist")
        print("Database integrity verified")

    def tearDown(self):
        """Clean up database connections"""
        print(f"--- Completing Test: {self._testMethodName} ---")
        if hasattr(self, 'db'):
            self.db.close_all_connections()

if __name__ == '__main__':
    unittest.main()
