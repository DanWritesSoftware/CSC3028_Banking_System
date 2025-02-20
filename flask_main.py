"""
flask_main.py
This script initializes and runs the Flask banking application.
"""

import os
import logging
from flask import Flask, render_template, request, redirect, flash, session
from flask_session import Session
from user_management import UserManager

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)

# Flask-Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "default_secret_key")
Session(app)

# Initialize user manager
user_manager = UserManager()

@app.route('/')
def home():
    """Render the home page with password reset link."""
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        result = user_manager.login(username, password)

        if result and result.get('requires_2fa'):
            session['2fa_email'] = result['email']
            return redirect('/verify_2fa')

        flash('Invalid credentials' if result is None else '2FA required', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        result = user_manager.sign_up(username, email, password, confirm_password)
        if "successfully" in result.lower():
            flash(result, 'success')
            return redirect('/login')
        flash(result, 'error')
    return render_template('register.html')

@app.route('/password-reset', methods=['GET', 'POST'])
def password_reset():
    """Handle password reset requests."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        result = user_manager.password_reset(username, email, new_password, confirm_password)
        if "successfully" in result.lower():
            flash(result, 'success')
            return redirect('/login')
        flash(result, 'error')
    return render_template('passwordReset.html')

@app.route('/new-account', methods=['GET', 'POST'])
def new_account():
    """Handle new account creation."""
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect('/login')

    if request.method == 'POST':
        account_data = user_manager.create_account(session['user_id'])
        if account_data:
            flash(f'Account created! Number: {account_data["account_number"]}', 'success')
            return redirect('/home')
        flash('Account creation failed', 'error')
    return render_template('newAccount.html')

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
            session['user_id'] = user['user_id']
            session['username'] = user['username']
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

if __name__ == '__main__':
    app.run(debug=True)