source# Banking Application

A secure and efficient banking system built with Flask, SQLite, and robust authentication mechanisms, including password hashing and two-factor authentication (2FA).

## Features

- **User Authentication**
  - Secure registration and login with hashed passwords.
  - Two-Factor Authentication (2FA) via email verification.
  - Secure session management with Flask-Session.
  
- **Account Management**
  - Create user accounts with unique IDs.
  - Retrieve and display user accounts.
  - Perform deposits and withdrawals with validation.
  - Transfer funds between accounts.

- **Account Types**
  - **Savings Accounts**: Manage savings with interest rates.
  - **Checking Accounts**: Standard checking account operations.
  - **Investing Accounts**: Handle investments and related transactions.

- **Security**
  - Password complexity enforcement.
  - Protection against SQL injection via parameterized queries.
  - Secure email-based 2FA.

## Project Structure

```
/banking-app
│── .idea/                 # IDE settings
│── .vscode/               # VS Code settings
│── __pycache__/           # Compiled Python files
│── flask_session/         # Session storage
│── static/                # Static assets (CSS, JS, images)
│── templates/             # HTML templates for frontend
│── Account.py             # Account class representation
│── BankingDatabase.db     # SQLite database file
│── BankingDatabase.sqbpro # SQLite database project file
│── Checking.py            # Handles checking account operations
│── Investing.py           # Handles investing account operations
│── Savings.py             # Handles savings account operations
│── User.py                # Represents a user in the banking system
│── database_handler.py    # Handles database operations
│── deposit_handler.py     # Manages deposit transactions
│── withdrawal_handler.py   # Manages withdrawal transactions
│── transfer_handler.py    # Manages fund transfers between accounts
│── flask_main.py          # Initializes and runs the Flask application
│── input_validator.py     # Validates user input
│── input_validator_test.py # Unit tests for input validation
│── selenium_tests.py       # End to end browser test (Selenium)
│── session_manager.py     # Manages user sessions
│── session_manager_test.py # Unit tests for session management
│── temp_account_holder.py  # Manages temporary account holders
│── user_management.py     # Handles user authentication and management
│── user_management_test.py # Unit tests for user management
│── requirements.txt       # List of project dependencies
│── README.md              # Project documentation
```

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/banking-app.git
   cd banking-app
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Run the Flask application:
   ```sh
   python flask_main.py
   ```

4. Open the application in your browser:
   ```
   http://127.0.0.1:5000
   ```

## Running Selenium Tests

To run the Selenium tests for the application, follow these steps:

1. **Ensure the Flask Application is Running**:
   - Open a terminal and navigate to the project directory.
   - Run the Flask application with:
     ```sh
     FLASK_ENV=testing python flask_main.py
     ```

2. **Run the Selenium Tests**:
   - Open another terminal and navigate to the project directory.
   - Execute the following command to run the Selenium tests:
     ```sh
     python selenium_tests.py
     ```

3. **Review Test Results**:
   - Check the terminal output for the results of the tests, including any successes or failures.

## Dependencies

- Flask
- Flask-Session
- bcrypt
- selenium
- requests

Install them with:
```sh
pip install -r requirements.txt
