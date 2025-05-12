from encryption_utils import decrypt_string_with_file_key
from audit_log import AuditLog

def mask_and_decrypt(log: AuditLog) -> dict:
    """Return a masked and decrypted view of an audit log entry."""
    try:
        old_value = decrypt_string_with_file_key(log.oldValue)
        new_value = decrypt_string_with_file_key(log.newValue)
    except Exception:
        old_value = new_value = "[Encrypted]"

    return {
        "Operation": log.Operation,
        "TableName": log.TableName,
        "oldValue": old_value[:50] + "..." if len(old_value) > 50 else old_value,
        "newValue": new_value[:50] + "..." if len(new_value) > 50 else new_value,
        "ChangedAt": log.ChangedAt,
        "signature": log.signature[:10] + "..." if log.signature else "[No Signature]"
    }

def mask_and_decrypt_all(logs: list[AuditLog]) -> list[dict]:
    """Process all logs into masked, safe-to-display versions."""
    return [mask_and_decrypt(log) for log in logs]
