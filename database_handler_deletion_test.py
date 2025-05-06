import os
import uuid
from hashlib import sha256
from database_handler import Database
from encryption_utils import encrypt_string_with_file_key
from datetime import datetime

DUMMY_DB = "DummyData.db"
DUMMY_BACKUP = "DummyDataBackup.db"
KEY_PATH = "encryption_key.key"

dummy_db = Database(name=DUMMY_DB, backup_name=DUMMY_BACKUP)

def init_full_schema(db: Database):
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS Role (
        RoleID INTEGER NOT NULL PRIMARY KEY,
        RoleName TEXT
    );

    CREATE TABLE IF NOT EXISTS SecurityLevels (
        levelID INTEGER PRIMARY KEY,
        title TEXT NOT NULL UNIQUE,
        clearanceRank INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS User (
        usrID INTEGER PRIMARY KEY,
        usrName TEXT,
        email TEXT,
        password TEXT,
        RoleID INTEGER,
        usrNameHash TEXT,
        emailHash TEXT
    );

    CREATE TABLE IF NOT EXISTS Account (
        accID TEXT NOT NULL PRIMARY KEY,
        accValue TEXT,
        accType TEXT,
        usrID INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS auditLog (
        ID INTEGER NOT NULL PRIMARY KEY,
        Operation TEXT,
        TableName TEXT,
        oldValue TEXT,
        newValue TEXT,
        ChangedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        signature TEXT
    );

    CREATE TABLE IF NOT EXISTS auditUserCreationLog (
        ID INTEGER PRIMARY KEY,
        usrID TEXT,
        email TEXT,
        password TEXT
    );
    """)
    conn.commit()
    print("[+] Full schema created.")

def insert_dummy_records(db: Database):
    conn = db.get_connection()
    cursor = conn.cursor()

    # Add a Role and Security Level
    cursor.execute("INSERT INTO Role (RoleID, RoleName) VALUES (?, ?)", (1, "Admin"))
    cursor.execute("INSERT INTO SecurityLevels (levelID, title, clearanceRank) VALUES (?, ?, ?)", (1, "Top Secret", 10))

    uid = str(uuid.uuid4().int)[:10]
    email = f"user{uid}@example.com"
    username = f"user{uid}"
    password = "testpass123"
    role_id = 1
    username_hash = sha256(username.encode()).hexdigest()
    email_hash = sha256(email.encode()).hexdigest()

    encrypted_usr_name = encrypt_string_with_file_key(username)
    encrypted_email = encrypt_string_with_file_key(email)

    db.create_user(uid, encrypted_usr_name, encrypted_email, password, role_id, username_hash, email_hash)
    db.create_account(acc_id=uid, usr_id=uid, acc_name="Checking", acc_balance=1000.00)

    print(f"[+] Inserted dummy user and account with usrID: {uid}")

def corrupt_database(db_path: str):
    with open(db_path, 'wb') as f:
        f.write(b'')  # Wipe DB contents
    print("[!] Database file corrupted.")

def run_full_backup_restore_demo():
    print("=== FULL SCHEMA BACKUP/RESTORE TEST ===")
    init_full_schema(dummy_db)
    insert_dummy_records(dummy_db)

    print("[*] Backing up encrypted dummy DB...")
    if dummy_db.backup_encrypted_database(KEY_PATH):
        print("[+] Backup created.")

    print("[*] Corrupting DB file...")
    corrupt_database(DUMMY_DB)

    print("[*] Restoring from backup...")
    if dummy_db.restore_encrypted_backup(KEY_PATH):
        print("[+] Database restored successfully.")

if __name__ == "__main__":
    run_full_backup_restore_demo()
