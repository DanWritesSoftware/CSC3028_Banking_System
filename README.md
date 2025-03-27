# Banking Application

A secure and efficient banking system built with Flask, SQLite, and robust authentication mechanisms, including password hashing and two-factor authentication (2FA). This application allows users to manage their accounts, perform transactions, and ensures security through various validation and logging mechanisms.

## Features
- **User Management**: 
  - Signup, login, and two-factor authentication (2FA) for enhanced security.
- **Account Management**: 
  - Create, retrieve, and manage user accounts, including savings, checking, and investing accounts.
- **Transaction Handling**: 
  - Perform deposits, withdrawals, and fund transfers with validation.
- **Logging**: 
  - Track application events and errors with logging functionality.
- **Input Validation**: 
  - Ensure all user inputs are validated to prevent errors and security issues.
- **Security**: 
  - Password complexity enforcement and protection against SQL injection.

## Testing
The application includes a comprehensive suite of tests to ensure functionality and security:
- **Unit Tests**: 
  - Tests for user management, input validation, deposit, withdrawal, and transfer functionalities.
- **Performance Tests**: 
  - Tests for user registration, login, account creation, and transaction workflows.
- **Edge Case Tests**: 
  - Tests for maximum and minimum transaction limits, invalid account formats, and SQL injection attempts.
- **End-to-End Tests**: 
  - Full workflow tests covering user registration, login, account management, and financial transactions.

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
│── selenium_tests.py      # End-to-end browser tests (Selenium)
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

## Running Tests
To run the tests for the application, follow these steps:

1. **Ensure the Flask Application is Running**:
   - Open a terminal and navigate to the project directory.
   - Run the Flask application with:
     ```sh
     FLASK_ENV=testing python flask_main.py
     ```

2. **Run the Unit Tests**:
   - Execute the following command to run the unit tests:
     ```sh
     python -m unittest discover
     ```

3. **Run the Selenium Tests**:
   - Open another terminal and navigate to the project directory.
   - Execute the following command to run the Selenium tests:
     ```sh
     python selenium_tests.py
     ```

4. **Review Test Results**:
   - Check the terminal output for the results of the tests, including any successes or failures.

## Dependencies
- Flask
- Flask-Session
- bcrypt
- selenium
- requests
- locust
- beautifulsoup4

Install them with:
```sh
pip install -r requirements.txt
