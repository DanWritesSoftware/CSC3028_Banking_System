import sys
import getpass
import os
import base64
import hashlib
from cryptography.fernet import Fernet

KEY_FILE = "encryption_key.key"

def derive_key(password):
    """Generate a Fernet-compatible key from a user password."""
    hashed_password = hashlib.sha256(password.encode()).digest()  # Hash password
    return base64.urlsafe_b64encode(hashed_password[:32])  # Make Fernet-compatible key

def load_or_generate_key(password):
    """Load the encryption key, or generate one if it doesn't exist."""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as key_file:
            stored_key = key_file.read()
        derived_key = derive_key(password)
        if stored_key != derived_key:
            print("Incorrect password! Decryption failed!")
            sys.exit(1)
        return derived_key
    else:
        key = derive_key(password)
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        return key

def encrypt_log(log_file, password):
    """Encrypt the log file using a password-derived key."""
    key = load_or_generate_key(password)
    cipher = Fernet(key)
    with open(log_file, "rb") as file:
        encrypted_data = cipher.encrypt(file.read())
    with open(log_file + ".enc", "wb") as enc_file:
        enc_file.write(encrypted_data)
    print(f"Log file encrypted: {log_file}.enc")

def decrypt_log(encrypted_log_file, password):
    """Decrypt the log file using a password-derived key."""
    key = load_or_generate_key(password)
    cipher = Fernet(key)
    with open(encrypted_log_file, "rb") as enc_file:
        decrypted_data = cipher.decrypt(enc_file.read())
    decrypted_filename = encrypted_log_file.replace(".enc", "_decrypted.log")
    with open(decrypted_filename, "wb") as dec_file:
        dec_file.write(decrypted_data)

    print(f"Log file decrypted: {decrypted_filename}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python log_encryptor.py <encrypt/decrypt> <log_file>")
        sys.exit(1)

    action = sys.argv[1].lower()
    log_file = sys.argv[2]
    password = getpass.getpass("🔑 Enter password: ")

    if action == "encrypt":
        encrypt_log(log_file, password)
    elif action == "decrypt":
        decrypt_log(log_file, password)
    else:
        print("Invalid action. Use 'encrypt' or 'decrypt'.")
