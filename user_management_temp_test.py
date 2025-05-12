import os
import bcrypt
import hashlib
from encryption_utils import decrypt_string_with_file_key, encrypt_string_with_file_key
from user_management import UserManager
from database_handler import Database

# Initialize components
db = Database("BankingData.db")
user_manager = UserManager()

# Test Parameters
username = "SecureUser"
email = f"{username}@example.com"
password = "StrongPass123!"
confirm_password = "StrongPass123!"

print("[TEST] Registering new secure user...")
result = user_manager.sign_up_customer(username, email, password, confirm_password)
print(f"[RESULT] Signup result: {result}")

print("\n[TEST] Looking up user with full decryption (slow)...")
decrypted_result = db.get_user_by_username(username)
if decrypted_result:
    print(f"[PASS] Decryption lookup successful: {decrypted_result['usrName']}")
else:
    print("[FAIL] Decryption lookup failed.")

print("\n[TEST] Looking up user with hash-based search (fast)...")
hash_result = db.get_user_encrypted_search(username)
if hash_result:
    print(f"[PASS] Encrypted search succeeded: {hash_result['usrName']}")
else:
    print("[FAIL] Encrypted search via hash failed.")

print("\n[TEST] Verifying password hash...")
if bcrypt.checkpw(password.encode(), hash_result['password'].encode()):
    print("[PASS] Password hash matches.")
else:
    print("[FAIL] Password hash mismatch.")

print("\n[TEST] Attempting login with encrypted search and 2FA trigger...")
login_result = user_manager.login(username, password)
if login_result and login_result.get('requires_2fa'):
    print(f"[PASS] Login succeeded. 2FA sent to: {login_result['email']}")
else:
    print("[FAIL] Login or 2FA trigger failed.")
