import os
import random
from database_handler import Database
from encryption_utils import decrypt_string_with_file_key
from user_management import UserManager

# Initialize components
db = Database("BankingData.db")
um = UserManager()

# Generate random test credentials
test_user = "testUser" + ''.join(random.choices('0123456789', k=6))
test_email = f"{test_user}@example.com"
test_password = "Pass123!" + ''.join(random.choices('0123456789', k=3))
acc_type = "Checking"
starting_balance = 1000.00
transfer_amount = 250.00

# Create test user and get the assigned user_id
print("[TEST] Creating test user...")
try:
    test_user_id = um.sign_up_customer(test_user, test_email, test_password, test_password)
    if test_user_id:
        print(f"[PASS] Test user created with ID: {test_user_id}")
    else:
        print("[FAIL] Failed to create test user.")
        exit()
except Exception as e:
    print(f"[FAIL] Exception during user creation: {e}")
    exit()

# Create two accounts for the user
print("[TEST] Creating two encrypted accounts...")
try:
    acc1_id = ''.join(random.choices('0123456789', k=10))
    acc2_id = ''.join(random.choices('0123456789', k=10))

    success1 = db.create_account(acc1_id, test_user_id, acc_type, starting_balance)
    success2 = db.create_account(acc2_id, test_user_id, acc_type, starting_balance)

    if success1 and success2:
        print("[PASS] Both accounts created successfully.")
    else:
        print("[FAIL] Account creation failed.")
except Exception as e:
    print(f"[FAIL] Exception during account creation: {e}")
