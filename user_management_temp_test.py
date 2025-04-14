# user_management_temp_test.py

from user_management import UserManager
import logging

# Setup logging to console
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Create instance of UserManager
user_manager = UserManager()

# Replace this with a valid user ID from your database
test_user_id = "9444219395"  # Use an actual usrID from your DB
test_index = 0  # First account

def test_get_user_account_info():
    logging.info(f"Testing get_user_account_info_from_index for user_id={test_user_id}, index={test_index}")
    result = user_manager.get_user_account_info_from_index(test_user_id, test_index)
    
    if result:
        logging.info(f"Retrieved account: Number={result.accountNumber}, Type={result.type}, Balance={result.balance}")
    else:
        logging.error("Failed to retrieve account information.")

if __name__ == "__main__":
    test_get_user_account_info()
