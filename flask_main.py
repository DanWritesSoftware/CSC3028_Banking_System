"""
flask_main.py
This script initializes and runs the Flask banking application.
"""

import os
import time
import random
import logging
from functools import wraps
from flask import Flask, render_template, request, redirect, flash, session
from flask_session import Session
from user_management import UserManager
from session_manager import SessionManager
from transfer_handler import Transfer
from deposit_handler import Deposit
from withdrawal_handler import Withdrawal
from memory_manager import MemoryManager
from input_validator import InputValidator
from encryption_utils import decrypt_string_with_file_key, mask_email, mask_username, mask_account_number
from audit_log_utils import mask_and_decrypt_all

# Initialize Flask Application
app = Flask(__name__)

# Environment Configuration
env = os.getenv('FLASK_ENV', '').lower()
app.config.update(
    SECRET_KEY=os.getenv("SECRET_KEY", "default-secret-key"),
    SESSION_TYPE="filesystem",
    TESTING=(env == 'testing'),
    WTF_CSRF_ENABLED=(env != 'testing'),
    DEBUG=(env == 'development')
)

# Initialize Extensions
Session(app)

# Application Components
session_manager = SessionManager()
user_manager = UserManager()
memory_manager = MemoryManager()
failed_login_attempts = {}

# RBAC Configuration
ROLES = {
    1: 'admin',
    2: 'teller',
    3: 'customer'
}

def requires_role(allowed_roles):
    """Role-Based Access Control Decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                flash('Authentication required', 'error')
                return redirect('/login')
                
            user_role = session.get('role_id')
            if user_role not in allowed_roles:
                flash('Insufficient privileges', 'error')
                logging.warning(f"Unauthorized access attempt by {session.get('username')} to {request.path}")
                return redirect('/home')
                
            return func(*args, **kwargs)
        return wrapper
    return decorator

@app.before_request
def init_memory_tracking():
    """Initialize memory tracking for each request"""
    memory_manager.register_object(f"request_{request.method}_{request.path}", request)
    memory_manager.baseline = memory_manager._get_memory_usage()

@app.after_request
def check_memory_leaks(response):
    """Check for memory leaks after each request"""
    if memory_manager.check_for_leaks():
        logging.error("Potential memory leak detected after %s %s", 
                     request.method, request.path)
    memory_manager.cleanup()
    return response

@app.route('/')
def default():
    """Root redirect based on authentication"""
    if not session_manager.is_authenticated():
        return redirect('/login')
    return redirect('/home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login with memory tracking"""
    memory_manager.register_object("login_processor", locals())
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        result = user_manager.login(username, password)

        if result and result.get('requires_2fa'):
            session['2fa_email'] = result['email']
            return redirect('/verify-2fa')
        if result:
            failed_login_attempts.pop(username, None)
            return redirect('/home')
        else:
            handle_failed_login(username)
            
    memory_manager.check_for_leaks()
    return render_template('login.html')

@app.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    """Two-Factor Authentication Verification"""
    if '2fa_email' not in session:
        flash('Authentication session expired', 'error')
        return redirect('/login')

    if request.method == 'POST':
        code = request.form.get('code')
        email = session['2fa_email']
        user = user_manager.verify_2fa(email, code)

        if user:
            session['user_id'] = user['usrID']
            session['username'] = decrypt_string_with_file_key(user['usrName'])
            session['role_id'] = user['RoleID']
            session.pop('2fa_email', None)

            if user['RoleID'] == 1:
                return redirect('/admin')
            elif user['RoleID'] == 2:
                return redirect('/teller-home')
            else:
                return redirect('/home')

        flash('Invalid verification code', 'error')
    return render_template('verify_2fa.html')

@app.route('/logout')
def logout():
    """Session termination endpoint"""
    username = session.get('username', 'unknown')
    logging.info(f"User {username} logged out.")
    session.clear()
    return redirect('/')

@app.route('/home')
@requires_role([3])
def customer_dashboard():
    """Customer dashboard with memory validation"""
    try:
        account_array = user_manager.get_database().get_user_accounts(session.get('user_id'))
        memory_manager.register_object("customer_accounts", account_array)
        validation_errors = validate_accounts(account_array)
        
        if validation_errors:
            for error in validation_errors:
                flash(error, 'error')
            return render_template('error.html')
            
        return render_template('home.html', 
                            account_list=[{
                                'number': mask_account_number(acc.accountNumber),
                                'type': acc.type,
                                'balance': acc.balance
                            } for acc in account_array
                            ],
                            username=mask_username(session.get('username')))
    except Exception as e:
        memory_manager.cleanup()
        logging.error(f"Memory error in customer dashboard: {str(e)}")
        return render_template('error.html')

@app.route('/teller')
@requires_role([1, 2])
def teller_dashboard():
    """Teller dashboard with memory checks"""
    memory_manager.register_object("teller_dashboard", session)
    return render_template('tellerHome.html', 
                         username=session.get('username'))

@app.route('/admin')
@requires_role([1])
def admin_dashboard():
    """Admin dashboard with resource monitoring"""
    memory_manager.register_object("admin_dashboard", session)
    log_list = user_manager.get_database().get_audit_logs()
    return render_template('admin_home.html', 
                         username=session.get('username'),
                         log_list=log_list)

# --------------------------
# Account Management Routes
# --------------------------
@app.route('/account-lookup', methods=['GET', 'POST'])
@requires_role([1, 2])
def teller_account_lookup():
    """Account lookup functionality for tellers"""
    memory_manager.register_object("account_lookup", locals())
    account_info_list = []
    usr_id = None

    if request.method == 'POST':
        usr_id = request.form.get('usr_id')
        try:
            accounts = user_manager.get_database().get_user_accounts(usr_id)
            for i, acc in enumerate(accounts):
                account_info_list.append({
                    'index': i,
                    'type': acc.type,
                    'number': acc.accountNumber(acc.accountNumber),
                    'balance': acc.balance
                })
            memory_manager.register_object("found_accounts", account_info_list)
        except Exception as e:
            flash(f"Error retrieving accounts: {str(e)}", 'error')

    return render_template('teller_account_lookup.html', 
                         accounts=account_info_list, 
                         usr_id=usr_id)

@app.route('/account/<usr_id>/<int:account_index>')
@requires_role([1, 2])
def teller_view_account(usr_id, account_index):
    """Account detail view for tellers"""
    try:
        account_info = user_manager.get_user_account_info_from_index(usr_id, account_index)
        memory_manager.register_object("viewed_account", account_info)
        
        return render_template('account_details.html',
                             account_number=account_info.accountNumber(account_info.accountNumber),
                             account_name=account_info.type,
                             account_value=account_info.balance,
                             usr_id=usr_id,
                             index=account_index)
    except IndexError:
        flash('Invalid account index', 'error')
    except Exception as e:
        flash(f"Error retrieving account: {str(e)}", 'error')
    return render_template('error.html')

@app.route('/transfer', methods=['GET','POST'])
@requires_role([1, 2, 3])
def transfer():
    """Funds transfer with resource tracking"""
    memory_manager.register_object("transfer_handler", locals())
    
    if request.method == 'POST':
        from_acc = request.form['fromAccountId']
        to_acc = request.form['toAccountId']
        amount = float(request.form['transferAmount'])
        
        transfer_obj = Transfer(from_acc, to_acc, amount, user_manager.get_database())
        memory_manager.register_object("transfer_instance", transfer_obj)
        
        errors = transfer_obj.try_transfer()
        handle_transfer_errors(errors, from_acc, to_acc, amount)
        
        memory_manager.check_for_leaks()
        return redirect('/home')
        
    return render_template('transfer.html')

@app.route('/deposit', methods=['GET','POST'])
@requires_role([1, 2])
def deposit():
    """Deposit handling with memory checks"""
    memory_manager.register_object("deposit_handler", locals())
    
    if request.method == 'POST':
        account_id = request.form['accountId']
        amount = float(request.form['depositAmount'])
        
        deposit_obj = Deposit(account_id, amount, user_manager.get_database())
        memory_manager.register_object("deposit_instance", deposit_obj)
        
        errors = deposit_obj.try_deposit()
        handle_deposit_errors(errors, account_id, amount)
        
        memory_manager.check_for_leaks()
        return redirect('/home')
        
    return render_template('deposit.html')

@app.route('/withdraw', methods=['GET','POST'])
@requires_role([1, 2])
def withdraw():
    """Withdrawal handling with resource management"""
    memory_manager.register_object("withdraw_handler", locals())
    
    if request.method == 'POST':
        account_id = request.form['accountId']
        amount = float(request.form['withdrawAmount'])
        
        withdrawal_obj = Withdrawal(account_id, amount, user_manager.get_database())
        memory_manager.register_object("withdrawal_instance", withdrawal_obj)
        
        errors = withdrawal_obj.try_withdrawal()
        handle_withdrawal_errors(errors, account_id, amount)
        
        memory_manager.check_for_leaks()
        return redirect('/home')
        
    return render_template('withdrawal.html')

# --------------------------
# User Management Routes
# --------------------------
@app.route('/register', methods=['GET', 'POST'])
def signup():
    """Customer registration endpoint"""
    memory_manager.register_object("signup_handler", locals())
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')

        result = user_manager.sign_up_customer(username, email, password, confirm_password)
        if "successfully" in result.lower():
            flash(result, 'success')
            return redirect('/login')
        flash(result, 'error')
    
    return render_template('register.html')

@app.route('/registerTeller', methods=['GET', 'POST'])
@requires_role([1])
def register_teller():
    """Teller registration endpoint"""
    memory_manager.register_object("teller_registration", locals())
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')

        result = user_manager.sign_up_teller(username, email, password, confirm_password)
        if "successfully" in result.lower():
            flash(result, 'success')
            return redirect('/admin')
        flash(result, 'error')
    
    return render_template('registerTeller.html')

@app.route('/registerAdmin', methods=['GET', 'POST'])
@requires_role([1])
def register_admin():
    """Admin registration endpoint"""
    memory_manager.register_object("admin_registration", locals())
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')

        result = user_manager.sign_up_admin(username, email, password, confirm_password)
        if "successfully" in result.lower():
            flash(result, 'success')
            return redirect('/admin')
        flash(result, 'error')
    
    return render_template('registerAdmin.html')

# --------------------------
# Admin Specfic Routes
# --------------------------

@app.route('/logs')
@requires_role([1])
def view_logs():
    """Admin only audit log viewer with masked output"""
    logs = user_manager.get_database().get_audit_logs()
    masked_logs = mask_and_decrypt_all(logs)
    return render_template('logs.html', logs=masked_logs, username=session.get('username'))



@app.route('/password-reset', methods=['GET', 'POST'])
@requires_role([1, 2, 3])
def password_reset():
    """Password reset functionality"""
    memory_manager.register_object("password_reset_handler", locals())
    
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
    
    return render_template('passwordReset.html')

@app.route('/system/status')
@requires_role([1])
def system_status():
    """Memory and resource status dashboard"""
    status = {
        'memory_usage': memory_manager._get_memory_usage(),
        'active_objects': len(memory_manager.object_registry),
        'connections': memory_manager.object_registry.get('database_connections', 0),
        'failed_logins': sum(failed_login_attempts.values())
    }
    return render_template('system_status.html', status=status)

@app.route('/system/cleanup')
@requires_role([1])
def system_cleanup():
    """Manual memory cleanup endpoint"""
    memory_manager.cleanup()
    flash("Memory cleanup performed", 'success')
    return redirect('/system/status')

def handle_failed_login(username):
    """Track failed login attempts with memory management"""
    failed_login_attempts[username] = failed_login_attempts.get(username, 0) + 1
    flash('Invalid credentials', 'error')
    
    if failed_login_attempts[username] >= 3:
        logging.error("Security alert: Multiple failed logins for %s", username)
        memory_manager.register_object(f"locked_account_{username}", {
            'attempts': failed_login_attempts[username],
            'timestamp': time.time()
        })

def validate_accounts(accounts):
    """Account validation with input checking"""
    validator = InputValidator()
    errors = []
    for acc in accounts:
        if not validator.validate_account_number(acc.accountNumber):
            errors.append(f"Invalid account: {acc.accountNumber}")
    memory_manager.register_object("validation_errors", errors)
    return errors

def handle_transfer_errors(errors, from_acc, to_acc, amount):
    """Transfer error handling with memory tracking"""
    if errors:
        memory_manager.register_object("transfer_errors", errors)
        for error in errors:
            flash(error, 'error')
        logging.warning("Transfer failed: %s", errors)
    else:
        logging.info("Successful transfer: %s from %s to %s", amount, from_acc, to_acc)
        flash('Transfer successful!', 'success')

def handle_deposit_errors(errors, account_id, amount):
    """Deposit error handling with resource management"""
    if errors:
        memory_manager.register_object("deposit_errors", errors)
        for error in errors:
            flash(error, 'error')
        logging.error("Deposit failed: %s", errors)
    else:
        logging.info("Successful deposit: %s to %s", amount, account_id)
        flash('Deposit successful!', 'success')

def handle_withdrawal_errors(errors, account_id, amount):
    """Withdrawal error handling with memory tracking"""
    if errors:
        memory_manager.register_object("withdrawal_errors", errors)
        for error in errors:
            flash(error, 'error')
        logging.error("Withdrawal failed: %s", errors)
    else:
        logging.info("Successful withdrawal: %s from %s", amount, account_id)
        flash('Withdrawal successful!', 'success')

if __name__ == '__main__':
    use_ssl = os.getenv('USE_SSL', 'false').lower() == 'true'
    debug_mode = env == 'development'

    if use_ssl:
        cert_path = os.path.join('certs', 'flask.crt')
        key_path = os.path.join('certs', 'flask.key')
        if os.path.exists(cert_path) and os.path.exists(key_path):
            print("[INFO] Starting Flask with SSL context")
            app.run(host='0.0.0.0', port=5000, debug=debug_mode, ssl_context=(cert_path, key_path))
        else:
            print("[ERROR] SSL enabled but cert/key files not found. Falling back to HTTP.")
            app.run(host='0.0.0.0', port=5000, debug=debug_mode)
    else:
        print("[INFO] Starting Flask without SSL (HTTP mode)")
        app.run(host='0.0.0.0', port=5000, debug=debug_mode)
