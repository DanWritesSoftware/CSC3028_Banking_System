# temp_database_handler_test.py

from database_handler import Database
from signature_utils import verify_signature
from datetime import datetime

# === CONFIG ===
DB_PATH = "BankingData.db"
ACCOUNT_1 = "1058260139"  # Replace with a real account ID
ACCOUNT_2 = "8750535125"  # Replace with a real account ID
TEST_AMOUNT = 25.00

# === INIT ===
db = Database(DB_PATH)

# === TEST DEPOSIT ===
print("[TEST] Depositing to ACCOUNT_1")
deposit_errors = db.deposit_to_account(ACCOUNT_1, TEST_AMOUNT)
if deposit_errors:
    print("[FAIL] Deposit Errors:", deposit_errors)
else:
    print("[PASS] Deposit successful.")

# === TEST WITHDRAW ===
print("\n[TEST] Withdrawing from ACCOUNT_1")
withdraw_errors = db.withdraw_from_account(ACCOUNT_1, TEST_AMOUNT)
if withdraw_errors:
    print("[FAIL] Withdrawal Errors:", withdraw_errors)
else:
    print("[PASS] Withdrawal successful.")

# === TEST TRANSFER ===
print("\n[TEST] Transferring from ACCOUNT_1 to ACCOUNT_2")
transfer_errors = db.transfer_funds_by_account_number(ACCOUNT_1, ACCOUNT_2, TEST_AMOUNT)
if transfer_errors:
    print("[FAIL] Transfer Errors:", transfer_errors)
else:
    print("[PASS] Transfer successful.")

# === AUDIT LOG VERIFICATION ===
print("\n[INFO] Verifying latest audit log entries:")
logs = db.get_audit_logs()
latest = logs[-3:]  # Expecting 3 entries: deposit, withdrawal, transfer x2

for i, log in enumerate(latest, 1):
    message = f"{log.Operation}|{log.TableName}|{log.oldValue}|{log.newValue}|{log.ChangedAt}"
    is_valid = verify_signature(message, bytes.fromhex(log.signature))
    print(f"  Log {i}: Operation={log.Operation}, Signature Valid? {is_valid}")

