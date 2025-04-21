import base64
import hashlib
from cryptography.fernet import Fernet
from key_manager import load_or_create_key, rotate_key, get_cipher

KEY_FILE = "encryption_key.key"

def encrypt_string_with_file_key(data: str) -> str:
    """Encrypts a string using the file-based key."""
    cipher = get_cipher()
    return cipher.encrypt(data.encode()).decode()

def decrypt_string_with_file_key(encrypted: str) -> str:
    """Decrypts a string using the file-based key."""
    cipher = get_cipher()
    return cipher.decrypt(encrypted.encode()).decode()

def rotate_encryption_key():
    """Rotate the encryption key with backup"""
    return rotate_key()
