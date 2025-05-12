import os
import random
from database_handler import Database
from encryption_utils import decrypt_string_with_file_key
from user_management import UserManager

# Initialize components
db = Database("BankingData.db")
um = UserManager()

# Generate random test credentials


db.get_user_accounts(7637531772)
