import base64
import hashlib
from cryptography.fernet import Fernet
from key_manager import load_or_create_key, rotate_key, get_cipher
from cryptography.fernet import Fernet

KEY_FILE = "encryption_key.key"

def encrypt_bytes_with_file_key(data: bytes) -> bytes:
    """Encrypt raw bytes using the Fernet key from file."""
    with open("encryption_key.key", "rb") as key_file:
        key = key_file.read()
    cipher = Fernet(key)
    return cipher.encrypt(data)

def encrypt_string_with_file_key(data: str) -> str:
    """Encrypts a string using the file-based key."""
    cipher = get_cipher()
    return cipher.encrypt(data.encode()).decode()

def mask_email(email: str) -> str:
    """Masks an email name"""
    try:
        local, domain = email.split('@')
        masked_local = local [0] + "***" if len(local) > 1 else "***"
        domain_parts = domain.split('.')
        masked_domain = domain_parts[0][0] + "***"
        if len (domain_parts) > 1:
            masked_domain += "." + domain_parts[1]
        return f"{masked_local}@{masked_domain}"
    except Exception:
        return "***@***"
    
def mask_account_number(account_number: str) -> str:
    """Masks Account Number to show only the last 4 digits."""
    if len(account_number) <= 4:
        return "****"
    return "*" * (len(account_number) - 4) + account_number[-4:]

def mask_username(username: str) -> str:
    """Masks a username to only show the first and last characters"""
    if len(username) <= 2:
        return "*" * len(username)
    return username[0] + "*" * (len(username) - 2) + username[-1:]


def decrypt_string_with_file_key(encrypted: str) -> str:
    """Decrypts a string using the file-based key."""
    cipher = get_cipher()
    return cipher.decrypt(encrypted.encode()).decode()

def rotate_encryption_key():
    """Rotate the encryption key with backup"""
    return rotate_key()
