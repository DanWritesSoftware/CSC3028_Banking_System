"""
Integration tests for banking system workflows.
Verifies database interactions and full transaction flows.
"""

import unittest
import sqlite3
import os
from database_handler import Database
from deposit_handler import Deposit
from withdrawal_handler import Withdrawal
from transfer_handler import Transfer

class TestBankingIntegration(unittest.TestCase):
    """Test cases for verifying integrated banking system functionality."""

    @classmethod
    def setUpClass(cls):
        """Create fresh test database with proper schema"""
        print("\n=== Initializing Test Database ===")
        cls.db_name = "test_banking.db"
        if os.path.exists(cls.db_name):
            os.remove(cls.db_name)

        # Create tables using the EXACT schema expected by Database class
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
        """Initialize test data for each test"""
        print(f"\n--- Initializing Test {self._testMethodName} ---")
        self.db = Database(self.db_name)

        # Clear existing data
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("DELETE FROM Account")
            conn.execute("DELETE FROM User")
            conn.commit()

        # Create test user and accounts
        self.user_id = "123"
        self.account1 = "1234567890"
        self.account2 = "0987654321"

        print("Creating test user and accounts...")
        self.db.create_user(
            self.user_id,
            "testuser",
            "test@example.com",
            "ValidPass123!"
        )
        self.db.create_account(self.account1, self.user_id, "Checking", 1000.0)
        self.db.create_account(self.account2, self.user_id, "Savings", 500.0)
        print(f"Created Checking: {self.account1} ($1000)")
        print(f"Created Savings: {self.account2} ($500)")

    def get_account_balance(self, account_id: str) -> float:
        """Directly get balance from database"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT accValue FROM Account WHERE accID=?", (account_id,))
            result = cursor.fetchone()
            return float(result[0]) if result else 0.0

    def test_full_deposit_flow(self):
        """Test complete deposit workflow"""
        print("\n[Deposit Test] Starting...")
        initial_balance = self.get_account_balance(self.account1)
        print(f"Initial balance: ${initial_balance:.2f}")

        print(f"Attempting deposit of $200 to {self.account1}")
        deposit = Deposit(self.account1, 200.0, self.db)
        result = deposit.try_deposit()

        self.assertEqual(result, [], "Deposit should have no errors")
        print("Deposit successful with no errors")

        new_balance = self.get_account_balance(self.account1)
        print(f"New balance: ${new_balance:.2f}")
        self.assertEqual(new_balance, 1200.0, "Balance should be $1200 after deposit")
        print("[Deposit Test] Completed successfully")

    def test_full_withdrawal_flow(self):
        """Test complete withdrawal workflow"""
        print("\n[Withdrawal Test] Starting...")
        initial_balance = self.get_account_balance(self.account1)
        print(f"Initial balance: ${initial_balance:.2f}")

        print(f"Attempting withdrawal of $300 from {self.account1}")
        withdrawal = Withdrawal(self.account1, 300.0, self.db)
        result = withdrawal.try_withdrawal()

        self.assertEqual(result, [], "Withdrawal should have no errors")
        print("Withdrawal successful with no errors")

        new_balance = self.get_account_balance(self.account1)
        print(f"New balance: ${new_balance:.2f}")
        self.assertEqual(new_balance, 700.0, "Balance should be $700 after withdrawal")
        print("[Withdrawal Test] Completed successfully")

    def test_full_transfer_flow(self):
        """Test complete transfer workflow"""
        print("\n[Transfer Test] Starting...")
        initial_source = self.get_account_balance(self.account1)
        initial_dest = self.get_account_balance(self.account2)
        print(f"Initial balances - Source: ${initial_source:.2f}, Dest: ${initial_dest:.2f}")

        print(f"Attempting transfer of $300 from {self.account1} to {self.account2}")
        transfer = Transfer(self.account1, self.account2, 300.0, self.db)
        result = transfer.try_transfer()

        self.assertEqual(result, [], "Transfer should have no errors")
        print("Transfer successful with no errors")

        new_source = self.get_account_balance(self.account1)
        new_dest = self.get_account_balance(self.account2)
        print(f"New balances - Source: ${new_source:.2f}, Dest: ${new_dest:.2f}")
        self.assertEqual(new_source, 700.0, "Source balance should be $700")
        self.assertEqual(new_dest, 800.0, "Destination balance should be $800")
        print("[Transfer Test] Completed successfully")

    def test_insufficient_funds_withdrawal(self):
        """Test insufficient funds handling"""
        print("\n[Insufficient Funds Test] Starting...")
        initial_balance = self.get_account_balance(self.account1)
        print(f"Initial balance: ${initial_balance:.2f}")

        print(f"Attempting withdrawal of $1500 from {self.account1}")
        withdrawal = Withdrawal(self.account1, 1500.0, self.db)
        result = withdrawal.try_withdrawal()

        print("Verifying error handling...")
        self.assertIn("Error: Insufficient Funds", result, "Should detect insufficient funds")
        print("Proper error detected")

        final_balance = self.get_account_balance(self.account1)
        print(f"Final balance: ${final_balance:.2f}")
        self.assertEqual(final_balance, 1000.0, "Balance should remain unchanged")
        print("[Insufficient Funds Test] Completed successfully")

if __name__ == '__main__':
    unittest.main()
