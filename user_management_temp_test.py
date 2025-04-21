# user_management_temp_test.py

from user_management import UserManager
import logging

# Setup logging to console
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Create instance of UserManager
user_manager = UserManager()

#user_manager.sign_up_customer("EncryptedTestUser", "Encrypterino@test.com", "ThisHasWorked2!", "ThisHasWorked2!")

user_manager.login("EncryptedTestUser", "ThisHasWorked2!")
