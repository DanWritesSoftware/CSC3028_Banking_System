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
def home():
    """Render the home page."""
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
            return redirect('/verify-2fa')

        flash('Invalid credentials' if result is None else '2FA required, not triggered', 'error')
    return render_template('login.html')

@app.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    """Handle 2FA verification."""
    if request.method == 'POST':
        code = request.form.get('code')
        email = session.get('2fa_email')

        if not email:
            flash('Session expired, please login again', 'error')
            return redirect('/login')

        user_data = user_manager.verify_2fa(email, code)
        if user_data:
            session['user_id'] = user_data['usrID']
            session.pop('2fa_email', None)
            return redirect('/dashboard')

        flash('Invalid verification code', 'error')
    return render_template('verify_2fa.html')

@app.route('/logout')
def logout():
    """Log out the user and clear session data."""
    session.clear()
    logging.info("User logged out.")
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    """Render the dashboard for logged-in users."""
    if 'user_id' not in session:
        flash('You must be logged in to view this page', 'error')
        return redirect('/login')
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user registration."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        result = user_manager.sign_up(username, email, password, confirm_password)
        if result == "User registered successfully!":
            flash(result, 'success')
            return redirect('/login')
        flash(result, 'error')
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)
