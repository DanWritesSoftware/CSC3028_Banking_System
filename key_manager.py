import os
import base64
from cryptography.fernet import Fernet
from datetime import datetime

KEY_FILE = "encryption_key.key"
BACKUP_DIR = "key_backups"

def generate_new_key() -> bytes:
    return Fernet.generate_key()

def backup_existing_key():
    if not os.path.exists(KEY_FILE):
        return
    
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"key_{timestamp}.bak")
    os.rename(KEY_FILE, backup_path)
    print(f"[INFO] Old Key backed up to: {backup_path}")

def load_or_create_key() -> bytes:
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            key = f.read()
            if len(key) != 44:
                raise ValueError ("Invalid Fernet key length")
            return key
        
    key = generate_new_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    print("[INFO] Encryption key generated and saved")

    return key

def rotate_key():
    backup_existing_key()
    new_key = generate_new_key()
    with open(KEY_FILE, "wb") as f:
        f.write(new_key)
    print ("[INFO] Encryption key rotated successfully")

    return new_key

def get_cipher() -> Fernet:
    key = load_or_create_key()
    return Fernet(key)
