import os
import gc
import time
import tempfile
import hashlib
from database_handler import Database
from encryption_utils import encrypt_string_with_file_key

def run_backup_restore_test():
    print("[TEST] Encrypted Backup and Restore")

    # Create unique temp paths instead of using NamedTemporaryFile
    db_fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)  # Close the file descriptor so SQLite can access it
    backup_path = temp_db_path + ".bak"
    key_path = "encryption_key.key"

    test_usr_id = "USR_TEST_BACKUP"
    test_acc_id = "ACC_TEST_BACKUP"

    try:
        # Step 1: Create DB and schema
        db = Database(temp_db_path)
        with db.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS User (
                    usrID TEXT PRIMARY KEY,
                    usrName TEXT,
                    email TEXT,
                    password TEXT,
                    RoleID INTEGER,
                    usrNameHash TEXT,
                    emailHash TEXT
                )""")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS Account (
                    accID TEXT PRIMARY KEY,
                    accType TEXT,
                    usrID TEXT,
                    accValue TEXT
                )""")
            conn.commit()

        # Step 2: Insert data
        encrypted_usrname = encrypt_string_with_file_key("backupuser")
        encrypted_email = encrypt_string_with_file_key("backup@test.com")
        usr_hash = hashlib.sha256("backupuser".encode()).hexdigest()
        email_hash = hashlib.sha256("backup@test.com".encode()).hexdigest()

        db.create_user(test_usr_id, encrypted_usrname, encrypted_email, "secure123", 3, usr_hash, email_hash)
        db.create_account(test_acc_id, test_usr_id, "Checking", 1000.00)

        # Step 3: Backup
        if db.backup_encrypted_database(backup_path, key_path):
            print("[PASS] Encrypted backup created.")
        else:
            print("[FAIL] Backup failed.")
            return

        # Step 4: Simulate data loss
        with db.get_connection() as conn:
            conn.execute("DELETE FROM Account")
            conn.execute("DELETE FROM User")
            conn.commit()

        # Step 5: Restore
        if db.restore_encrypted_backup(backup_path, key_path):
            print("[PASS] Database restored.")
        else:
            print("[FAIL] Restore failed.")
            return

        # Step 6: Reset DB object
        db.close_all_connections()
        del db
        gc.collect()
        time.sleep(0.1)  # Let the OS release handles

        db = Database(temp_db_path)

        # Step 7: Verify restoration
        restored_accounts = db.get_user_accounts(test_usr_id)
        if len(restored_accounts) == 1 and restored_accounts[0].accountNumber == test_acc_id:
            print("[PASS] Data restoration verified.")
        else:
            print("[FAIL] Restored data does not match.")

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")

    finally:
        # Final cleanup
        if 'db' in locals():
            db.close_all_connections()
            del db
        gc.collect()
        time.sleep(0.1)

        try:
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)
            if os.path.exists(backup_path):
                os.remove(backup_path)
            print("[CLEANUP] Temporary DB files removed.")
        except Exception as cleanup_error:
            print(f"[ERROR] Cleanup failed: {cleanup_error}")

if __name__ == "__main__":
    run_backup_restore_test()
