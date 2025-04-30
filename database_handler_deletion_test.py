import os
import tempfile
import hashlib
import secrets
from database_handler import Database
from encryption_utils import encrypt_string_with_file_key

def setup_temp_database():
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    db = Database(temp_db.name)
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS User (
            usrID TEXT PRIMARY KEY,
            usrName TEXT,
            email TEXT,
            password TEXT,
            RoleID INTEGER,
            usrNameHash TEXT,
            emailHash TEXT
        );
        CREATE TABLE IF NOT EXISTS Account (
            accID TEXT PRIMARY KEY,
            accType TEXT,
            usrID TEXT,
            accValue TEXT
        );
        CREATE TABLE IF NOT EXISTS auditLog (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Operation TEXT,
            TableName TEXT,
            oldValue TEXT,
            newValue TEXT,
            ChangedAt TEXT,
            signature TEXT
        );
    """)
    conn.commit()
    return db, temp_db.name

def insert_test_data(db, user_id, account_id):
    username = "TestUser"
    email = "test@example.com"
    password = secrets.token_hex(16)

    encrypted_name = encrypt_string_with_file_key(username)
    encrypted_email = encrypt_string_with_file_key(email)
    username_hash = hashlib.sha256(username.encode()).hexdigest()
    email_hash = hashlib.sha256(email.encode()).hexdigest()

    db.get_cursor().execute(
        "INSERT INTO User VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, encrypted_name, encrypted_email, password, 3, username_hash, email_hash)
    )

    acc_type = encrypt_string_with_file_key("Checking")
    acc_value = encrypt_string_with_file_key("999.99")

    db.get_cursor().execute(
        "INSERT INTO Account VALUES (?, ?, ?, ?)",
        (account_id, acc_type, user_id, acc_value)
    )
    db.get_connection().commit()

def run_deletion_tests():
    db, path = setup_temp_database()

    assert "BankingData.db" not in db.name, " Refusing to test on production database!"

    user_id = "USR_TEST_0001"
    acc_id = "ACC_TEST_0001"

    insert_test_data(db, user_id, acc_id)

    print("[TEST] secure_delete_account()")
    assert db.secure_delete_account(acc_id), "secure_delete_account() failed"
    acc_row = db.get_cursor().execute("SELECT * FROM Account WHERE accID = ?", (acc_id,)).fetchone()
    assert acc_row is None, "Account was not fully deleted"
    print("[PASS] Account deleted securely.")

    print("[TEST] secure_delete_user()")
    assert db.secure_delete_user(user_id), "secure_delete_user() failed"
    user_row = db.get_cursor().execute("SELECT * FROM User WHERE usrID = ?", (user_id,)).fetchone()
    assert user_row is None, "User was not fully deleted"
    print("[PASS] User deleted securely.")

    db.close_all_connections()
    os.remove(path)
    print("[CLEANUP] Temporary DB connection closed and file removed.")

if __name__ == "__main__":
    run_deletion_tests()
