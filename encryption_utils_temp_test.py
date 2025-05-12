from encryption_utils import encrypt_string_with_file_key, decrypt_string_with_file_key

secret = "very sensitive info"
encrypted = encrypt_string_with_file_key(secret)
decrypted = decrypt_string_with_file_key(encrypted)

print("Encrypted:", encrypted)
print("Decrypted:", decrypted)
