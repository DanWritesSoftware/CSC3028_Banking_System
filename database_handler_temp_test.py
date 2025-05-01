import os
import random
from database_handler import Database
from encryption_utils import decrypt_string_with_file_key
from user_management import UserManager

# Initialize components
db = Database("BankingData.db")
um = UserManager()

# Generate random test credentials


# Create test user and get the assigned user_id
print("[TEST] Creating test user...")
try:
    test_user_id = um.sign_up_admin("overLord", "overLord@example.com", "Barbarian1!", "Barbarian1!")
    if test_user_id:
        print(f"[PASS] Test user created with ID: {test_user_id}")
    else:
        print("[FAIL] Failed to create test user.")
        exit()
except Exception as e:
    print(f"[FAIL] Exception during user creation: {e}")
    exit()

