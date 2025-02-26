"""
flask_main.py
This script initializes and runs the Flask banking application.
"""

import os
import logging
from flask import Flask, render_template, request, redirect, flash, session
from flask_session import Session
from user_management import UserManager
from session_manager import SessionManager
from transfer_handler import Transfer
from deposit_handler import Deposit
from withdrawal_handler import Withdrawal
from input_validator import InputValidator
import random # for account number generation

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)

# Flask-Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "default_secret_key")
Session(app)

# Initialize session manager and user manager
session_manager = SessionManager()
user_manager = UserManager()

@app.route('/')
def default():
    """Redirect to the home page."""
    return redirect('/home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        result = user_manager.login(username, password)

        if result and result.get('requires_2fa'):
            session['2fa_email'] = result['email']
            return redirect('/verify-2fa')

        flash('Invalid credentials' if result is None else '2FA required', 'error')
    return render_template('login.html')

@app.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    """Handle 2FA verification."""
    if '2fa_email' not in session:
        flash('Authentication session expired', 'error')
        return redirect('/login')

    if request.method == 'POST':
        code = request.form.get('code')
        email = session['2fa_email']
        user = user_manager.verify_2fa(email, code)

        if user:
            session['user_id'] = user['usrID']
            session['username'] = user['usrName']
            session.pop('2fa_email', None)
            return redirect('/home')

        flash('Invalid verification code', 'error')
    return render_template('verify_2fa.html')

@app.route('/logout')
def logout():
    """Clear session and logout user."""
    session.clear()
    logging.info("User logged out.")
    return redirect('/')

@app.route('/home')
def dashboard():
    """Render the dashboard for logged-in users."""
    if 'user_id' not in session:
        flash('You must be logged in to view this page', 'error')
        return redirect('/login')
    # Fetch user accounts
    account_array = user_manager.get_database().get_user_accounts(session.get('user_id'))
    # Initialize a list for error messages
    validation_errors = []
    valid = InputValidator()

    # Iterate through each account and validate
    for account in account_array:

        if not valid.validate_account_number(account.accountNumber):
            # Account Error
            validation_errors.append(f"ERROR READING DATA - Account number {account.accountNumber} is invalid.")

        if valid.validate_currency_amount(account.balance) == False:
            # Balance Error
            validation_errors.append(f"ERROR READING DATA - Balance for account {account.accountNumber} is invalid.")

    if validation_errors:
        # Show errors to user
        for error in validation_errors:
            flash(error, 'error')
            print(error)
        # redirect to error page where flashed messages are displayed.
        return render_template('error.html')

    return render_template('home.html', account_list=account_array, username=session.get('username'))

@app.route('/register', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('register.html')

    """Handle user registration."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')

        result = user_manager.sign_up(username, email, password, confirm_password)
        if result == "User registered successfully!":
            flash(result, 'success')
            return redirect('/login')
        flash(result, 'error')
    return render_template('register.html')
@app.route('/password-reset', methods=['GET', 'POST'])

def password_reset():
    # Handle user not logged in
    if 'user_id' not in session:
        flash('You must be logged in to view this page', 'error')
        return redirect('/login')

    if request.method == 'GET':
        # Load Form
        return render_template('passwordReset.html')

    """Handle password reset requests."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        result = user_manager.password_reset(username, email, new_password, confirm_password)
        if "successfully" in result.lower():
            flash(result, 'success')
            return redirect('/home')
        flash(result, 'error')
    return redirect('/password-reset')

@app.route('/transfer', methods=['GET','POST'])
def transfer():
    # Handle user not logged in
    if 'user_id' not in session:
        flash('You must be logged in to view this page', 'error')
        return redirect('/login')

    if request.method == 'GET':
        return render_template('transfer.html')

    if request.method == 'POST':
        fromAccountID = request.form['fromAccountId']
        toAccountID = request.form['toAccountId']
        transferAmount = request.form['transferAmount']
        t = Transfer(fromAccountID, toAccountID, float(transferAmount), user_manager.get_database())
        errors = t.try_transfer()
        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect('/transfer')
        else:
            flash('Transfer Success!')
            return redirect('/home')
        
@app.route('/deposit', methods=['GET','POST'])
def deposit():
    if request.method == 'GET':
        return render_template('deposit.html')

    accountID = request.form['accountId']
    depositAmount = request.form['depositAmount']
    d = Deposit(accountID, float(depositAmount), user_manager.get_database())
    errors = d.try_deposit()
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect('/deposit')
    else:
        flash('Deposit Success!')
        return redirect('/home')
    
@app.route('/withdraw', methods=['GET','POST'])
def withdraw():
    if request.method == 'GET':
        return render_template('withdrawal.html')

    accountID = request.form['accountId']
    withdrawAmount = request.form['withdrawAmount']
    w = Withdrawal(accountID, float(withdrawAmount), user_manager.get_database())
    errors = w.try_withdrawal()
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect('/withdraw')
    else:
        flash('Withdrawal Success!')
        return redirect('/home')

@app.route('/new', methods = ['POST', 'GET'])
def new():
    # Handle user not logged in
    if 'user_id' not in session:
        flash('You must be logged in to view this page', 'error')
        return redirect('/login')

    valid = InputValidator()

    if request.method == 'GET':
        # Load form
        return render_template('newAccount.html')
    if request.method == 'POST':
        # Get the account name and value from the form
        account_name = request.form['accountName']
        account_value = request.form['value']

        # Validate Input

        # Initialize a list for error messages
        validationErrors = []

        if not valid.validate_username(account_name):
            # Account name issue
            validationErrors.append(f"ERROR Account Name {account_name} is invalid. Please keep names between 5 and 20 Characters.")

        try:
            if not valid.validate_currency_amount(float(account_value)):
                # Currency issue
                validationErrors.append(f"ERROR Currency Value {account_value} is invalid. Please include the decimals after the whole number.")
        except ValueError:
            # Not a number
            validationErrors.append(f"ERROR Please Input Digits.")

        if validationErrors:
            # Flash errors
            for error in validationErrors:
                flash(error, 'error')
                print(error)
            # reload page to reset form and diaplay flashed errors.
            return redirect('/new')

        # Generate a new account number
        random_account = random.randint(1000000000, 9999999999)
        # Regenerate if in use
        while user_manager.get_database().user_id_in_use(str(random_account)):
            randomAccount = random.randint(1000000000, 999999999)

        # Create account in database
        #db.createAccount(randomAccount,1,accountName,accountValue)
        user_manager.get_database().create_account(str(random_account),session.get('user_id'), account_name, float(account_value))
        return redirect('/home')

if __name__ == '__main__':
    app.run(debug=True)
