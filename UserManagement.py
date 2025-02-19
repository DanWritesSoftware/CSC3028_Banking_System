from DatabaseHandler import Database
from input_validator import InputValidator
import hashlib
import random

# Create an instance of Database
db_manager = Database("BankingDatabase.db")

Input_Validator = InputValidator()

length = 10

class UserManager:
    def __init__(self):
        pass

    def signUp(self, userName:str, email:str, password:str, confirmPassword:str, userID:int):

        if not Input_Validator.validate_username(userName):
            print("Invalid username, try again")

        if not Input_Validator.validate_email(email):
            print("Invalid Email, try again")

        if not Input_Validator.validate_password_complexity(password):
            print("Password not complex enough, please try again")

        if confirmPassword != password:
            return ("Passwords do not match.")
        
        # Hash the password for security
        hash1 = hashlib.md5(password.encode()).hexdigest()

        while True:
            userID = ''.join(random.choices('0123456789', k = length))
            if not db_manager.accountIdInUse(userID):
                break

        db_manager.createUser(userID, userName, email, hash1)

        return (" User registered successfully!")


    def login(self, userName:str, password:str,):
        authorizerHash = hashlib.md5(password.encode()).hexdigest()

        try:
            if db_manager.userLogin(userName, authorizerHash):

                return("User Logged in Succesfully.")
            else:
                return("Username or Password incorrect, login failed")

        except Exception as e:
            return("Error logging in.")


