"""
End-to-end (E2E) tests for the Banking System using Selenium WebDriver.
This test suite covers user registration, login, account management, and financial transactions.
"""

import unittest
import time
import sqlite3  # Standard library import moved before third-party imports
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class BankingSystemE2ETest(unittest.TestCase):
    """
    End-to-end test suite for the Banking System.
    This class tests user registration, login, account management, and financial transactions.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up the test suite by initializing the WebDriver and test user credentials.
        """
        print("\n===== Initializing Test Suite =====")
        cls.driver = webdriver.Chrome()
        cls.base_url = "http://localhost:5000"
        cls.test_email = f"testuser{int(time.time())}@example.com"
        cls.test_password = "ValidPass123!"
        cls.test_username = f"testuser{int(time.time())}"
        print(f"Test User: {cls.test_username}")
        print(f"Test Email: {cls.test_email}")

    def setUp(self):
        """
        Prepare for each test by cleaning up previous test data and clearing browser cookies.
        """
        print("\n----- Starting New Test -----")
        print("Cleaning up previous test data...")
        self.cleanup_test_user()
        print("Clearing browser cookies...")
        self.driver.delete_all_cookies()

    def test_full_banking_workflow(self):
        """
        Test the full banking workflow, including registration, 
        login, account creation, and transactions.
        """
        try:
            print("\n=== Starting Full Workflow Test ===")
            # 1. User Registration
            print("\n--- Phase 1: User Registration ---")
            self.register_user()
            # 2. Login & 2FA Handling
            print("\n--- Phase 2: User Login & 2FA ---")
            self.login_with_2fa()
            # 3. Account Management
            print("\n--- Phase 3: Account Management ---")
            account_number = self.create_and_verify_account()
            # 4. Financial Transactions
            print("\n--- Phase 4: Financial Transactions ---")
            self.perform_transactions(account_number)
            # 5. Cleanup
            print("\n--- Phase 5: Post-Test Cleanup ---")
            self.cleanup_test_user()
            print("\n=== All Test Phases Completed Successfully ===")

        except Exception as e:
            print(f"\n!!! Test Failed: {str(e)}")
            print(f"Current URL: {self.driver.current_url}")
            print(f"Page source snippet:\n{self.driver.page_source[:2000]}")
            raise

    def register_user(self):
        """
        Simulate user registration by filling out and submitting the registration form.
        """
        print("Navigating to registration page")
        self.driver.get(f"{self.base_url}/register")

        print(f"Entering username: {self.test_username}")
        self.wait_and_send_keys(By.NAME, "username", self.test_username)

        print(f"Entering email: {self.test_email}")
        self.wait_and_send_keys(By.NAME, "email", self.test_email)

        print("Entering password (masked)")
        self.wait_and_send_keys(By.NAME, "password", self.test_password)

        print("Confirming password (masked)")
        self.wait_and_send_keys(By.NAME, "confirmPassword", self.test_password)

        print("Submitting registration form")
        self.click_submit(By.XPATH, "//input[@type='submit']")

        print("Verifying success message")
        self.wait_for_flash_message("User registered successfully!")

    def login_with_2fa(self):
        """
        Simulate user login and handle two-factor authentication (2FA).
        """
        print("Navigating to login page")
        self.driver.get(f"{self.base_url}/login")

        print(f"Entering username: {self.test_username}")
        self.wait_and_send_keys(By.NAME, "username", self.test_username)

        print("Entering password (masked)")
        self.wait_and_send_keys(By.NAME, "password", self.test_password)

        print("Submitting login form")
        self.click_submit(By.XPATH, "//input[@type='submit']")

        print("Waiting for 2FA page")
        WebDriverWait(self.driver, 15).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Two-Factor Authentication")
        )

        print("Retrieving verification code...")
        verification_code = self.retrieve_verification_code()
        print(f"Entering verification code: {verification_code}")
        self.wait_and_send_keys(By.NAME, "code", verification_code)

        print("Submitting 2FA form")
        self.click_submit(By.XPATH, "//button[@type='submit']")

        print("Verifying successful login")
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Logout"))
        )
        print("Login successful")

    def retrieve_verification_code(self):
        """
        Retrieve the 2FA verification code from the test endpoint.
        """
        print("Attempting to retrieve 2FA code...")
        for attempt in range(1, 11):
            print(f"Attempt {attempt}/10 to fetch verification code")
            response = requests.get(
                f"{self.base_url}/test/get_verification_code/{self.test_email}",
                timeout=10  # Added timeout
            )
            if response.status_code == 200:
                code = response.json()['code']
                print(f"Successfully retrieved code: {code}")
                return code
            time.sleep(0.5)
        raise TimeoutException("2FA code not received after 10 attempts")

    def create_and_verify_account(self):
        """
        Create a new bank account and verify its creation.
        """
        print("\nCreating new account")
        self.driver.get(f"{self.base_url}/new")

        print("Entering account name: Checking")
        self.wait_and_send_keys(By.NAME, "accountName", "Checking")

        print("Setting initial balance: 1000.00")
        self.wait_and_send_keys(By.NAME, "value", "1000.00")

        print("Submitting account creation form")
        self.click_submit(By.XPATH, "//input[@type='submit']")

        print("Verifying account creation success")
        self.wait_for_flash_message("Account created")
        print("Account created successfully")

        print("Validating home page redirect")
        WebDriverWait(self.driver, 15).until(EC.url_contains("/home"))
        print(f"Current URL: {self.driver.current_url}")

        print("Locating new account in dashboard")
        account_link = WebDriverWait(self.driver, 15).until(
        EC.element_to_be_clickable(
        (By.XPATH, "//h1[contains(text(), 'Checking')]/ancestor::div[@class='grid-item']/a")))
        account_link.click()

        print("Navigated to account details page")

        print("Extracting account number")
        account_number_element = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Account Number:')]"))
        )
        account_number = account_number_element.text.split(": ")[1]
        print(f"Found account number: {account_number}")

        print("Returning to home page")
        self.driver.get(f"{self.base_url}/home")
        return account_number

    def perform_transactions(self, account_number):
        """
        Perform deposit and withdrawal transactions.
        """
        print("\nProcessing deposit transaction")
        self.driver.get(f"{self.base_url}/deposit")

        print(f"Selecting account: {account_number}")
        self.wait_and_send_keys(By.NAME, "accountId", account_number)

        print("Entering deposit amount: 500.00")
        self.wait_and_send_keys(By.NAME, "depositAmount", "500.00")

        print("Submitting deposit form")
        self.click_submit(By.XPATH, "//input[@type='submit']")
        self.wait_for_flash_message("Deposit Success!")
        print("Deposit completed successfully")

        print("\nProcessing withdrawal transaction")
        self.driver.get(f"{self.base_url}/withdraw")

        print(f"Selecting account: {account_number}")
        self.wait_and_send_keys(By.NAME, "accountId", account_number)

        print("Entering withdrawal amount: 200.00")
        self.wait_and_send_keys(By.NAME, "withdrawAmount", "200.00")

        print("Submitting withdrawal form")
        self.click_submit(By.XPATH, "//input[@type='submit']")
        self.wait_for_flash_message("Withdrawal Success!")
        print("Withdrawal completed successfully")

    def wait_and_send_keys(self, by, locator: str, text: str):
        """
        Wait for an element to be present and send input text to it.
        """
        print(f"Waiting for element: {locator}")
        element = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((by, locator))
        )
        print(f"Entering text: {'*' * len(text) if 'password' in locator else text}")
        element.clear()
        element.send_keys(text)

    def click_submit(self, by, locator: str):
        """
        Wait for a submit button to be clickable and click it.
        """
        print(f"Looking for submit button: {locator}")
        element = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((by, locator)))
        print("Clicking submit button")
        element.click()
        time.sleep(0.5)  # Small delay for page transitions

    def wait_for_flash_message(self, message: str, timeout=15):
        """
        Wait for a flash message containing the specified text to appear.
        """
        print(f"Waiting for flash message containing: '{message}'")
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: any(message in msg.text for msg in d.find_elements(
                    By.CSS_SELECTOR, ".flash-message, .alert"))
            )
            print("Success message verified")
        except TimeoutException:
            print("!!! Missing expected flash message !!!")
            print(f"Current page content:\n{self.driver.page_source[:2000]}")
            raise

    def cleanup_test_user(self):
        """
        Clean up test data by deleting the test user and associated accounts from the database.
        """
        print("\nCleaning up test data from database")
        conn = sqlite3.connect("BankingDatabase.db")
        try:
            cursor = conn.cursor()
            print(f"Deleting user: {self.test_email}")
            user_delete = cursor.execute("DELETE FROM User WHERE email=?", (self.test_email,))
            print(f"Deleted {user_delete.rowcount} user(s)")

            print("Deleting associated accounts")
            account_delete = cursor.execute(
                "DELETE FROM Account WHERE accUserID IN (SELECT usrID FROM User WHERE email=?)",
                (self.test_email,))
            print(f"Deleted {account_delete.rowcount} account(s)")
            conn.commit()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @classmethod
    def tearDownClass(cls):
        """
        Clean up the test suite by closing the browser.
        """
        print("\n===== Terminating Test Suite =====")
        cls.driver.quit()
        print("Browser closed")


if __name__ == "__main__":
    unittest.main()
