from user_management import UserManager
from database_handler import Database
import logging
import os

# Setup logging to console
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Constants
DB_PATH = "BankingData.db"  # or whatever your DB name is
TEST_USERNAME = "SecureSearchUser"
TEST_EMAIL = "securesearch@example.com"
TEST_PASSWORD = "TestPass#456!"

# Init
user_manager = UserManager()
db = Database(DB_PATH)

# STEP 1: Register a new user
print("[TEST] Registering new secure user...")
signup_result = user_manager.sign_up_customer(
    username=TEST_USERNAME,
    email=TEST_EMAIL,
    password=TEST_PASSWORD,
    confirm_password=TEST_PASSWORD
)
print(f"[RESULT] Signup result: {signup_result}")

# STEP 2: Decryption-based lookup
print("\n[TEST] Looking up user with full decryption (slow)...")
user_decrypted = db.get_user_by_username(TEST_USERNAME)
if user_decrypted:
    print(f"[PASS] Decryption lookup successful: {user_decrypted['usrName']}")
else:
    print("[FAIL] Decryption lookup failed.")

# STEP 3: Hash-based encrypted lookup
print("\n[TEST] Looking up user with hash-based search (fast)...")
user_hashed = db.get_user_encrypted_search(TEST_USERNAME)
if user_hashed:
    print(f"[PASS] Encrypted search succeeded: {user_hashed['usrName']}")
else:
    print("[FAIL] Encrypted search via hash failed.")
