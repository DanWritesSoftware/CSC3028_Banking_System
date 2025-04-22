from signature_utils import sign_message, verify_signature

# Test message
message = "This is a digitally signed transaction."

# Sign it
signature = sign_message(message)
print("[INFO] Signature generated.")

# Verify it
is_valid = verify_signature(message, signature)
print(f"[RESULT] Signature valid? {is_valid}")

# Tampered message test
tampered_message = "This is a hacked transaction."
is_valid_tampered = verify_signature(tampered_message, signature)
print(f"[RESULT] Tampered message valid? {is_valid_tampered}")
