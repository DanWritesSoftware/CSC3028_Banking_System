import hashlib
from database_handler import Database

# Initialize database
db = Database("BankingData.db")

# Username for testing
username = "testuser1741464305"

# Print computed hash for debugging
username_hash = hashlib.sha256(username.lower().encode()).hexdigest()
print(f"[DEBUG] Computed hash: {username_hash}")

print("\n[TEST] Searching user with hash-based encrypted search (fast)...")
result = db.get_user_encrypted_search(username)

if result:
    print("[PASS] Encrypted search via hash succeeded.")
    print(f"User: {result['usrName']} | Email: {result['email']}")
else:
    print("[FAIL] Encrypted search via hash failed.")
