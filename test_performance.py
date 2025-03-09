"""
Complete performance test for banking system with dynamic account handling.
"""

import logging
import uuid
from locust import HttpUser, task, between
from locust.exception import StopUser
from bs4 import BeautifulSoup

class BankingUser(HttpUser):
    """Simulates complete user lifecycle with dynamic account creation."""
    
    wait_time = between(1, 5)
    host = "http://localhost:5000"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = f"loaduser_{uuid.uuid4().hex[:8]}"
        self.password = "LoadTest123!"
        self.email = f"{self.user_id}@test.com"
        self.primary_account = None
        self.secondary_account = None
        self.csrf_token = None
        self.session = self.client

    def on_start(self):
        """Full user initialization workflow"""
        try:
            # Get initial CSRF token
            self._get_csrf_token("/register")
            
            # Execute user lifecycle
            self._register()
            self._login()
            self._create_primary_account()
            self._create_secondary_account()
            
            logging.info("User %s initialized with accounts %s and %s", 
                        self.user_id, self.primary_account, self.secondary_account)
        except Exception as e:
            logging.error("Initialization failed: %s", str(e))
            raise StopUser()

    def _get_csrf_token(self, url):
        """Extract CSRF token from any page"""
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        token_input = soup.find('input', {'name': 'csrf_token'})
        self.csrf_token = token_input['value'] if token_input else ''

    def _register(self):
        """User registration workflow"""
        with self.session.post("/register", data={
            "username": self.user_id,
            "email": self.email,
            "password": self.password,
            "confirmPassword": self.password,
            "csrf_token": self.csrf_token
        }, catch_response=True) as response:
            if not response.ok:
                response.failure(f"Registration failed: {response.text}")

    def _login(self):
        """User login workflow"""
        self._get_csrf_token("/login")
        with self.session.post("/login", data={
            "username": self.user_id,
            "password": self.password,
            "csrf_token": self.csrf_token
        }, catch_response=True) as response:
            if not response.ok:
                response.failure(f"Login failed: {response.text}")

    def _create_account(self, account_name="PrimaryAccount"):
        """Generic account creation method"""
        self._get_csrf_token("/new")
        with self.session.post("/new", data={
            "accountName": account_name,
            "value": "1000.00",
            "csrf_token": self.csrf_token
        }, catch_response=True) as response:
            if response.ok:
                return self._extract_account_id()
            response.failure(f"Account creation failed: {response.text}")
        return None

    def _create_primary_account(self):
        """Create main operating account"""
        self.primary_account = self._create_account("PrimaryAccount")
        if not self.primary_account:
            raise StopUser("Primary account creation failed")

    def _create_secondary_account(self):
        """Create transfer recipient account"""
        self.secondary_account = self._create_account("SecondaryAccount")
        if not self.secondary_account:
            raise StopUser("Secondary account creation failed")

    def _extract_account_id(self):
        """Extract latest account ID from home page"""
        home_resp = self.session.get("/home")
        soup = BeautifulSoup(home_resp.text, 'html.parser')
        accounts = soup.find_all("div", class_="account-number")
        return accounts[-1].text.strip() if accounts else None

    @task(5)
    def deposit_withdraw_cycle(self):
        """Complete deposit/withdrawal workflow"""
        # Deposit
        self._get_csrf_token("/deposit")
        with self.session.post("/deposit", data={
            "accountId": self.primary_account,
            "depositAmount": "100.00",
            "csrf_token": self.csrf_token
        }, catch_response=True) as response:
            if "Deposit Success" not in response.text:
                response.failure("Deposit failed")

        # Withdrawal
        self._get_csrf_token("/withdraw")
        with self.session.post("/withdraw", data={
            "accountId": self.primary_account,
            "withdrawAmount": "50.00",
            "csrf_token": self.csrf_token
        }, catch_response=True) as response:
            if "Withdrawal Success" not in response.text:
                response.failure("Withdrawal failed")

    @task(3)
    def transfer_operations(self):
        """Complete transfer workflow between accounts"""
        self._get_csrf_token("/transfer")
        with self.session.post("/transfer", data={
            "fromAccountId": self.primary_account,
            "toAccountId": self.secondary_account,
            "transferAmount": "25.00",
            "csrf_token": self.csrf_token
        }, catch_response=True) as response:
            if "Transfer Success" not in response.text:
                response.failure("Transfer failed")

    @task(1)
    def error_scenarios(self):
        """Validate error handling"""
        # Invalid deposit amount
        self._get_csrf_token("/deposit")
        with self.session.post("/deposit", data={
            "accountId": self.primary_account,
            "depositAmount": "100.123",
            "csrf_token": self.csrf_token
        }, catch_response=True) as response:
            if "Invalid deposit amount" not in response.text:
                response.failure("Invalid deposit accepted")

    def on_stop(self):
        """Cleanup after user"""
        self.session.get("/logout")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)