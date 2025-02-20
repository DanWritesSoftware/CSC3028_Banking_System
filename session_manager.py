"""
session_manager.py
This module handles user session management, including login, logout, and authentication checks.
"""

import logging
from flask import session, flash

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class SessionManager:
    """Handles user session management."""

    @staticmethod
    def login_user(user_id: int, username: str) -> None:
        """Stores user information in the session."""
        session['user_id'] = user_id
        session['username'] = username
        logging.info("User %s logged in with session.", username)

    @staticmethod
    def logout_user() -> None:
        """Clears the session and logs the user out."""
        session.clear()
        flash("Logged out successfully.", "success")
        logging.info("User logged out.")

    @staticmethod
    def is_authenticated() -> bool:
        """Checks if the user is logged in."""
        return 'user_id' in session
