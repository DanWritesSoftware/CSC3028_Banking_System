import re
import sys
from datetime import datetime
import os
from cryptography.fernet import Fernet

KEY_FILE = "encryption_key.key"

def load_key():
    """Load encryption key from file."""
    try:
        with open(KEY_FILE, "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        print("Encryption key not found! Cannot decrypt logs!")
        sys.exit(1)

def decrypt_log(encrypted_log_file):
    """Decrypt the encrypted log file and return its content."""
    key = load_key()
    cipher = Fernet(key)
    with open(encrypted_log_file, "rb") as enc_file:
        decrypted_data = cipher.decrypt(enc_file.read())

    return decrypted_data.decode("utf-8").splitlines()

def search_logs(log_file, keyword=None, log_level=None, start_date=None, end_date=None):
    """
    Search logs based on keyword, log level, and date range.
    # Example usage:
    # #Search different keywords
    # python log_search.py banking_system.log "User not found" NONE NONE NONE
    # #Filter by log level
    # python log_search.py banking_system.log NONE WARNING NONE NONE
    # #Search by date range
    # python log_search.py banking_system.log NONE NONE "2025-03-07 16:42:00" "2025-03-07 16:50:00"
    """
    results = []
    try:
        with open(log_file, 'r', encoding='utf-8') as file:
            logs = file.readlines()
            print(f"Total logs found: {len(logs)}")

            for line in logs:
                match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) - (.*)$', line)
                if not match:
                    continue
                log_time, level, message = match.groups()
                log_time = datetime.strptime(log_time, "%Y-%m-%d %H:%M:%S,%f")

                if log_level and log_level.upper() != "NONE" and level != log_level:
                    continue
                if keyword and keyword.upper() != "NONE" and keyword.lower() not in message.lower():
                    continue
                if start_date and start_date.upper() != "NONE":
                    start_date_dt = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
                    if log_time < start_date_dt:
                        continue
                if end_date and end_date.upper() != "NONE":
                    end_date_dt = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
                    if log_time > end_date_dt:
                        continue
                results.append(line.strip())
    except Exception as e:
        print(f"Error reading log file: {e}")
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python log_search.py <log_file> <keyword> <log_level> <start_date> <end_date>")
        sys.exit(1)

    log_file = sys.argv[1]
    keyword = sys.argv[2] if len(sys.argv) > 2 else "NONE"
    log_level = sys.argv[3] if len(sys.argv) > 3 else "NONE"
    start_date = sys.argv[4] if len(sys.argv) > 4 else "NONE"
    end_date = sys.argv[5] if len(sys.argv) > 5 else "NONE"

    results = search_logs(log_file, keyword, log_level, start_date, end_date)

    if results:
        print("\n".join(results))
        with open("search_results.txt", "w", encoding="utf-8") as output_file:
            for result in results:
                output_file.write(result + "\n")
    else:
        print("No matching logs found.")
