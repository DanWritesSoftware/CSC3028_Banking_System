import base64
import hashlib
from cryptography.fernet import Fernet

KEY_FILE = "encryption_key.key"

def load_key_from_file() -> bytes:
    """Loads the Fernet key from a file."""
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()

def get_file_cipher() -> Fernet:
    """Returns a Fernet cipher using the file-based key."""
    key = load_key_from_file()
    return Fernet(key)

def encrypt_string_with_file_key(data: str) -> str:
    """Encrypts a string using the file-based key."""
    cipher = get_file_cipher()
    return cipher.encrypt(data.encode()).decode()

def decrypt_string_with_file_key(encrypted: str) -> str:
    """Decrypts a string using the file-based key."""
    cipher = get_file_cipher()
    return cipher.decrypt(encrypted.encode()).decode()
