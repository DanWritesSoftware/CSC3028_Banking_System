"""
Edge case validation for banking transactions.
Tests extreme values and unexpected inputs.
"""

import unittest
import sqlite3
import os
from database_handler import Database
from deposit_handler import Deposit
from withdrawal_handler import Withdrawal

class TestEdgeCases(unittest.TestCase):
    """Test cases for extreme values and malicious inputs"""
    
    @classmethod
    def setUpClass(cls):
        """Create dedicated test database with proper schema"""
        print("\n=== Initializing Edge Case Test Database ===")
        cls.db_name = "test_edge_cases.db"
        if os.path.exists(cls.db_name):
            os.remove(cls.db_name)
            
        # Create tables using production schema
        with sqlite3.connect(cls.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE User (
                    usrID TEXT PRIMARY KEY,
                    usrName TEXT NOT NULL,
                    email TEXT NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE Account (
                    accID TEXT PRIMARY KEY,
                    accType TEXT NOT NULL,
                    accUserID TEXT,
                    accValue REAL NOT NULL,
                    FOREIGN KEY (accUserID) REFERENCES User(usrID)
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

        # Create test accounts
        self.valid_account = "1234567890"
        print("Creating test user 'edgeuser' with account 1234567890 ($100.00)")
        self.db.create_user("edge123", "edgeuser", "edge@test.com", "EdgePass123!")
        self.db.create_account(self.valid_account, "edge123", "Checking", 100.0)

    def get_account_balance(self, account_id: str) -> float:
        """Directly get balance from database"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT accValue FROM Account WHERE accID=?", (account_id,))
            result = cursor.fetchone()
            return float(result[0]) if result else 0.0

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
            del self.db

if __name__ == '__main__':
    unittest.main()