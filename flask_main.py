"""
flask_main.py
This script initializes and runs the Flask banking application.
"""

import os
import time
import random
from flask import Flask, render_template, request, redirect, flash, session
from flask_session import Session
from user_management import UserManager
from session_manager import SessionManager
from transfer_handler import Transfer
from deposit_handler import Deposit
from withdrawal_handler import Withdrawal
from input_validator import InputValidator
from log_manager import logging

'''# Initialize Flask app
app = Flask(__name__)

logging.info("Logging system initialized.")
'''

app = Flask(__name__)
app.config["TESTING"] = True
logging.info("Logging system initialized.")


'''
# Configure environment-specific settings
if os.getenv('FLASK_ENV') == 'testing':
    # Testing configurations
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SECRET_KEY="test-secret-key",
        SESSION_TYPE="filesystem"
    )
else:
    # Production configurations
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "default-secret-key"),
        SESSION_TYPE="filesystem"
    )
    '''

env = os.getenv('FLASK_ENV', '').lower()

if env == 'testing':
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SECRET_KEY="test-secret-key",
        SESSION_TYPE="filesystem"
    )
elif env == 'development':
    app.config.update(
        DEBUG=True,
        TESTING = True,
        SECRET_KEY="dev-secret-key",
        SESSION_TYPE="filesystem"
    )
else:
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "default-secret-key"),
        SESSION_TYPE="filesystem"
    )


# Initialize session extension
Session(app)

# Initialize application components
session_manager = SessionManager()
user_manager = UserManager()

# To hold failed login attempts
failed_login_attempts = {}

@app.before_request
def log_request_info():
    logging.info(f"Incoming request: {request.method} {request.url} from {request.remote_addr}")

@app.after_request
def log_response_info(response):
    logging.info(f"Response status: {response.status_code} for {request.method} {request.url}")
    return response

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
        if result:
            logging.info(f"Successful login attempt for user: {username}")
            failed_login_attempts.pop(username, None)
        else:
            logging.warning(f"Failed login attempt for user: {username} from {request.remote_addr}")
            failed_login_attempts[username] = failed_login_attempts.get(username, 0) + 1
            flash('Invalid credentials' if result is None else '2FA required', 'error')

            if failed_login_attempts[username] >= 3:
                logging.error(f"SECURITY INCIDENT: More than three failed login attenpts for user: {username} from {request.remote_addr}")
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
            session['role_id'] = user['RoleID']
            session.pop('2fa_email', None)

            if user['RoleID'] == 3:
                return redirect('/customerHome')
            
            if user['RoleID'] == 2:
                return redirect('/tellerHome')
            
            if user['RoleID'] == 1:
                return redirect('/home')

        flash('Invalid verification code', 'error')
    return render_template('verify_2fa.html')

@app.route('/logout')
def logout():
    """Clear session and logout user."""
    #session.clear()
    username = session.get('username', 'unknown')
    logging.info(f"User {username} logged out.")
    session.clear()
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

        #if valid.validate_currency_amount(account.balance) == False:
            # Balance Error
            validation_errors.append(f"ERROR READING DATA - Balance for account {account.accountNumber} is invalid.")

    if validation_errors:
        # Show errors to user
        for error in validation_errors:
            flash(error, 'error')
            print(error)
        # redirect to error page where flashed messages are displayed.
        return render_template('error.html')

    return render_template('home.html', account_list=account_array,
                            username=session.get('username'))

@app.route('/customerHome')
def customerDashboard():
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

        #if valid.validate_currency_amount(account.balance) == False:
            # Balance Error
            validation_errors.append(f"ERROR READING DATA - Balance for account {account.accountNumber} is invalid.")

    if validation_errors:
        # Show errors to user
        for error in validation_errors:
            flash(error, 'error')
            print(error)
        # redirect to error page where flashed messages are displayed.
        return render_template('error.html')

    return render_template('customerHome.html', account_list=account_array,
                            username=session.get('username'))

@app.route('/tellerHome')
def tellerDashboard():
    """Render the dashboard for logged-in Tellers."""
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

        #if valid.validate_currency_amount(account.balance) == False:
            # Balance Error
            validation_errors.append(f"ERROR READING DATA - Balance for account {account.accountNumber} is invalid.")

    if validation_errors:
        # Show errors to user
        for error in validation_errors:
            flash(error, 'error')
            print(error)
        # redirect to error page where flashed messages are displayed.
        return render_template('error.html')

    return render_template('tellerHome.html', account_list=account_array,
                            username=session.get('username'))

@app.route('/register', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('register.html')

    #Handle user registration.
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')

        result = user_manager.sign_up_customer(username, email, password, confirm_password)
        if result == "User registered successfully!":
            flash(result, 'success')
            return redirect('/login')
        flash(result, 'error')
    return render_template('register.html')

@app.route('/registerTeller', methods=['GET', 'POST'])
def register_teller():
    if request.method == 'GET':
        return render_template('registerTeller.html')

    #Handle teller registration.
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')

        result = user_manager.sign_up_teller(username, email, password, confirm_password)
        if result == "Teller registered successfully!":
            flash(result, 'success')
            return redirect('/login')
        flash(result, 'error')
    return render_template('registerTeller.html')

@app.route('/registerAdmin', methods=['GET', 'POST'])
def register_Admin():
    if request.method == 'GET':
        return render_template('registerAdmin.html')

    #Handle teller registration.
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')

        result = user_manager.sign_up_admin(username, email, password, confirm_password)
        if result == "Administrator registered successfully!":
            flash(result, 'success')
            return redirect('/login')
        flash(result, 'error')
    return render_template('registerAdmin.html')

@app.route('/password-reset', methods=['GET', 'POST'])
def password_reset():
    # Handle user not logged in
    if 'user_id' not in session:
        flash('You must be logged in to view this page', 'error')
        return redirect('/login')

    if request.method == 'GET':
        # Load Form
        return render_template('passwordReset.html')

    # Handle password reset requests.
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
                logging.warning(f"Failed transfer attempt by {session['username']} from {fromAccountID} to {toAccountID}: {error}")
            return redirect('/transfer')
        else:
            logging.info(f"User {session['username']} transferred {transferAmount} from {fromAccountID} to {toAccountID}.")
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
        user_manager.get_database().create_account(str(random_account),
                    session.get('user_id'), account_name, float(account_value))
        flash("Account created successfully!", 'success')
        return redirect('/home')

@app.route('/account/<account_index>')
def account_details(account_index):
    # Handle user not logged in
    if 'user_id' not in session:
        flash('You must be logged in to view this page', 'error')
        return redirect('/login')

    # display account information
    try:
        user_id = session.get('user_id')
        account_info = user_manager.get_user_account_info_from_index(user_id,int(account_index))
    except IndexError:
        flash('It looks like you are lost. Try returning to the home page.', 'error')
        return render_template('error.html')
    except Exception as e:
        flash(f'An unexpected error occurred: {str(e)}', 'error')
        return render_template('error.html')
    account_number = account_info.accountNumber
    account_name = account_info.type
    account_value = account_info.balance
    return render_template('account_details.html', account_number = account_number,
                            account_name = account_name, account_value = account_value)

@app.route('/test/get_verification_code/<email>')
def test_get_verification_code(email):
    """Test endpoint to retrieve 2FA codes (testing only)"""
    if not app.config.get('TESTING'):
        return "Endpoint disabled in production", 403

    code_data = user_manager._verification_codes.get(email)
    if code_data and time.time() < code_data['expires']:
        return {'code': code_data['code']}
    return {'error': 'Code not found or expired'}, 404

if __name__ == '__main__':
    #app.run(debug=False) # Changed to false, for the log to show output
    app.run(debug=True) # Changed to true, in order to get the verification code on school wifi :3
