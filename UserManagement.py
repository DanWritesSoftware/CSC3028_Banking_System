from DatabaseHandler import Database
from User import User
import hashlib

# Create an instance of Database
db_manager = Database("BankingDatabase.db")

class UserManager:
    def __init__(self, name):
        self.name = name

    def signUp(self):

        special_characters = {'!', '@', '#', '$', '^', '&', '*', '(', ')'}

        email_validators = {'@' , '.com' , '.net' , '.gov' , '.edu'}

        while True:

            email = input("Enter a valid email address: ")

            if not any(char in email_validators for char in email):
                print("Please enter a valid email address. Try Again")
                continue

            password = input("Enter a password that contains a special character: ")

            # Check if password contains at least one special character
            if not any(char in special_characters for char in password):
                print(" Password must contain at least one special character. Try again!")
                continue  # Ask for password again
            
            confirmPassword = input("Please Re-Enter your password: ")

            if confirmPassword != password:
                print(" Error: Passwords do not match. Try again!")
                continue  # Ask for password again

            # If both conditions are met, exit the loop
            break

        # Hash the password for security
        hash1 = hashlib.md5(password.encode()).hexdigest()

        # Open file in APPEND mode ("a"), so it doesn't overwrite existing data
        with open("credentials.txt", "a") as file:
            file.write(email + "\n")  # Write email
            file.write(hash1 + "\n")  # Write hashed password
            file.write("---\n")  # Separator for clarity
            file.flush()  # Ensure immediate write

        print(" User registered successfully!")


    def login(self):
        email = input("Please Enter your email: ")
        password = input("Please enter your password: ")

        authorizerHash = hashlib.md5(password.encode()).hexdigest()

        try:
            with open("credentials.txt", "r") as file:
                lines = file.readlines()
            
            for i in range(0, len(lines), 3):
                storedEmail = lines[i].strip()
                storedPassword = lines[i +1].strip()

                if email == storedEmail and authorizerHash == storedPassword:
                    print("Log in Succesful!")
                    return
            print("Login failed, invalid email or password.")

        except FileNotFoundError:
            print(" Error: No user registered yet. Please sign up first.")


# Create an instance of UserManager and call the different functions
user_manager = UserManager("TestUser")

user_manager.signUp()













