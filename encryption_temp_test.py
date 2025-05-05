from cryptography.fernet import Fernet

key = open("encryption_key.key", "rb").read()
cipher = Fernet(key)

# Replace with one of your failing accValue strings
sample = b"gAAAAABoGP4k7TfOHdycC-znOAe3dJcQEIXZWg7w7GyjDIL5XDeFZyv0uvgfqvFHLN_wxOoNqqmX5_gomXKuGA_tlPF8Yl0PmA=="

try:
    result = cipher.decrypt(sample).decode()
    print("[SUCCESS]", result)
except Exception as e:
    print("[FAILED]", e)
