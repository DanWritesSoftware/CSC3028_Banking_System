import logging
import os
import atexit
import subprocess
import sys

# Ensure logs directory exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
LOG_FILE = os.path.join(LOG_DIR, "banking_system.log")

# Ensure log file exists (prevents errors)
if not os.path.exists(LOG_FILE):
    open(LOG_FILE, "w").close()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ],
    force=True  # Ensures old handlers don’t interfere
)
# Get logger instance
logger = logging.getLogger()

def encrypt_log_on_exit():
    """Function to encrypt log file on exit."""
    print("Encrypting log file before exiting application...")
    subprocess.run([sys.executable, "log_encryptor.py", "encrypt", LOG_FILE])

# Run when Flask exits
atexit.register(encrypt_log_on_exit)