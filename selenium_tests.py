"""
End-to-end (E2E) tests for the Banking System using Selenium WebDriver.
Syntax-correct version with proper parentheses.
"""

import unittest
import time
import sqlite3
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from database_handler import Database

class BankingSystemE2ETest(unittest.TestCase):
    """
    Working end-to-end test suite with proper syntax.
    """

    @classmethod
    def setUpClass(cls):
        """Initialize test suite with proper configuration"""
        print("\n===== Initializing Test Suite =====")
        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(2)
        cls.base_url = "http://localhost:5000"
        cls.test_email = f"testuser{int(time.time())}@example.com"
        cls.test_password = "ValidPass123!"
        cls.test_username = f"testuser{int(time.time())}"
        cls.db = Database("BankingData.db")

    def setUp(self):
        """Prepare for each test with proper cleanup"""
        print("\n----- Starting New Test -----")
        self.cleanup_test_user()
        self.driver.delete_all_cookies()
        self.driver.get(f"{self.base_url}/logout")

    def test_full_banking_workflow(self):
        """Complete banking workflow test"""
        try:
            print("\n=== Starting Full Workflow Test ===")
            
            # 1. User Registration
            self.driver.get(f"{self.base_url}/register")
            self._send_keys_safe(By.NAME, "username", self.test_username)
            self._send_keys_safe(By.NAME, "email", self.test_email)
            self._send_keys_safe(By.NAME, "password", self.test_password)
            self._send_keys_safe(By.NAME, "confirmPassword", self.test_password)
            self._click_safe(By.CSS_SELECTOR, "input[type='submit']")
            self._verify_flash_message("User registered successfully!")

            # 2. Login & 2FA
            self.driver.get(f"{self.base_url}/login")
            self._send_keys_safe(By.NAME, "username", self.test_username)
            self._send_keys_safe(By.NAME, "password", self.test_password)
            self._click_safe(By.CSS_SELECTOR, "input[type='submit']")
            
            # Handle 2FA (fixed syntax)
            WebDriverWait(self.driver, 10).until(
                EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Two-Factor Authentication")
            )
            code = self._retrieve_verification_code()
            self._send_keys_safe(By.NAME, "code", code)
            self._click_safe(By.XPATH, "//button[contains(text(), 'Verify')]")
            self._verify_element_present(By.LINK_TEXT, "Logout")

            # 3. Account Management
            account_number = self._create_bank_account()
            
            # 4. Transactions
            self._perform_deposit(account_number)
            self._perform_withdrawal(account_number)

            print("\n=== Test Completed Successfully ===")

        except Exception as e:
            self._capture_failure_state()
            raise

    def _create_bank_account(self):
        """Create and verify new bank account"""
        self.driver.get(f"{self.base_url}/new")
        self._send_keys_safe(By.NAME, "accountName", "Checking")
        self._send_keys_safe(By.NAME, "value", "1000.00")
        self._click_safe(By.CSS_SELECTOR, "input[type='submit']")
        self._verify_flash_message("Account created successfully!")

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT accID FROM Account WHERE usrID=?", (self._get_user_id(),))
            return cursor.fetchone()[0]

    def _perform_deposit(self, account_number):
        """Execute deposit transaction"""
        self.driver.get(f"{self.base_url}/deposit")
        self._send_keys_safe(By.NAME, "accountId", account_number)
        self._send_keys_safe(By.NAME, "depositAmount", "500.00")
        self._click_safe(By.CSS_SELECTOR, "input[type='submit']")
        self._verify_flash_message("Deposit Success!")

    def _perform_withdrawal(self, account_number):
        """Execute withdrawal transaction"""
        self.driver.get(f"{self.base_url}/withdraw")
        self._send_keys_safe(By.NAME, "accountId", account_number)
        self._send_keys_safe(By.NAME, "withdrawAmount", "200.00")
        self._click_safe(By.CSS_SELECTOR, "input[type='submit']")
        self._verify_flash_message("Withdrawal Success!")

    def _get_user_id(self):
        """Retrieve user ID from database"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT usrID FROM User WHERE email=?", (self.test_email,))
            return cursor.fetchone()[0]

    def _retrieve_verification_code(self):
        """Get 2FA code with retry logic"""
        for _ in range(20):
            try:
                response = requests.get(
                    f"{self.base_url}/test/get_verification_code/{self.test_email}",
                    timeout=3
                )
                if response.status_code == 200:
                    return response.json()['code']
            except requests.RequestException:
                pass
            time.sleep(0.5)
        raise TimeoutException("Failed to retrieve 2FA code after 20 attempts")

    def _send_keys_safe(self, by, locator, text):
        """Robust text input with visibility check"""
        element = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((by, locator)))
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(0.05)

    def _click_safe(self, by, locator):
        """Reliable click with scroll into view"""
        element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((by, locator)))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.2)
        element.click()
        time.sleep(0.5)

    def _verify_flash_message(self, message):
        """Verify flash messages with content check"""
        WebDriverWait(self.driver, 10).until(
            lambda d: any(message in msg.text for msg in d.find_elements(By.CSS_SELECTOR, ".flash-message")))
        time.sleep(0.3)

    def _verify_element_present(self, by, locator):
        """Generic element presence verification"""
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((by, locator)))

    def cleanup_test_user(self):
        """Database cleanup using application's DB handler"""
        print("\nCleaning up test data...")
        with self.db.get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys=OFF")
                cursor.execute("DELETE FROM Account WHERE usrID IN (SELECT usrID FROM User WHERE email=?)", (self.test_email,))
                cursor.execute("DELETE FROM User WHERE email=?", (self.test_email,))
                cursor.execute("PRAGMA foreign_keys=ON")
                conn.commit()
            except sqlite3.Error as e:
                print(f"Cleanup error: {str(e)}")
                conn.rollback()

    def _capture_failure_state(self):
        """Debugging information capture"""
        print(f"\n!!! TEST FAILURE DETECTED !!!")
        print(f"Current URL: {self.driver.current_url}")
        print("Page Title:", self.driver.title)
        print("Relevant Page Content:")
        print(self.driver.page_source[:3000])
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT * FROM User WHERE email=?", (self.test_email,))
                print(f"User exists: {bool(cursor.fetchone())}")
            except sqlite3.Error as e:
                print(f"Database check error: {str(e)}")

    @classmethod
    def tearDownClass(cls):
        """Final cleanup"""
        print("\n===== Terminating Test Suite =====")
        cls.db.close_all_connections()
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main(failfast=True)