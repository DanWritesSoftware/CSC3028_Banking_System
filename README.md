# Banking Application

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
│── Checking.py            # Checking account operations
│── Investing.py           # Investing account operations
│── Savings.py             # Savings account operations
│── User.py                # User class representation
│── database_handler.py    # Handles database operations
│── flask_main.py          # Main Flask application
│── input_validator.py     # Validates user input
│── input_validator_test.py # Tests for input validation
│── session_manager.py     # Manages user sessions
│── session_manager_test.py # Tests for session management
│── temp_account_holder.py # Temporary account handling
│── transfer_handler.py    # Handles fund transfers
│── user_management.py     # Handles user authentication & 2FA
│── user_management_test.py # Tests for user management
│── requirements.txt       # Dependencies list
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

## Usage

### User Registration
- Users can sign up via `/signup`
- Validates username, email, and password complexity.
- Stores securely hashed passwords.

### User Login & 2FA
- Users log in via `/login`
- If login is successful, a 2FA email is sent.
- Users enter a 6-digit verification code on `/verify-2fa`

### Account Management
- Users can view their accounts on `/dashboard`
- Deposit and withdrawal operations are validated.

### Logout
- Users can log out via `/logout`, which clears the session.

## Security Features

- **Password Hashing**: Uses bcrypt to store passwords securely.
- **Two-Factor Authentication (2FA)**: Adds an extra layer of security.
- **Session Security**: Flask-Session ensures authenticated sessions.
- **Input Validation**: Prevents invalid or malicious input.

## Dependencies

- Flask
- Flask-Session
- bcrypt

Install them with:
```sh
pip install -r requirements.txt
```

