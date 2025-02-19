import sqlite3
from Account import Account

from User import User

class Database:
    def __init__(self, name):
        self.name = name
        # connection and cursor are now locally opened and closed with each class function
        #self.connection = sqlite3.connect(name, check_same_thread=False)
        #self.cursor = self.connection.cursor()

    def createAccount(self, accID: str, usrID: str, accName: str, accBalance: float):
        # Open a new connection and cursor
        connection = sqlite3.connect(self.name, check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO Account (accID, accType, accUserID, accValue) VALUES (?, ?, ?, ?)",
            (accID, accName, usrID, accBalance)
        )
        connection.commit()

        # close connection
        connection.close()
        return True
    
    def createUser(self, usrID: int, usrName: str, email: str, password: str):
        #open a new connection and cursor
        connection = sqlite3.connect(self.name, check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO User (usrID, usrName, email, password) VALUES (?, ?, ?, ?)",
            (usrID, usrName, email, password)
        )
        connection.commit()

        # close connection
        connection.close()
        return True

    def getUserAccounts(self, usrID: str):
        # Open a new connection and cursor
        connection = sqlite3.connect(self.name, check_same_thread=False)
        cursor = connection.cursor()

        # get all accounts matching with id
        cursor.execute("SELECT * FROM Account WHERE accUserID='"+str(usrID)+"'")
        rows = cursor.fetchall()

        # Create a list to store Account objects
        accounts = []

        # Iterate through each row and create an Account object
        for row in rows:
            accID = row[0]
            accValue = row[1]
            accType = row[2]
            account = Account(accID,accType,accValue)
            accounts.append(account)

        # close connection
        connection.close()

        return accounts
    
    def getUsers(self, usrID: str):
        # Open a new connection and cursor
        connection = sqlite3.connect(self.name, check_same_thread=False)
        cursor = connection.cursor()

        # get all accounts matching with id
        cursor.execute("SELECT * FROM User WHERE usrID='"+str(usrID)+"'")
        rows = cursor.fetchall()

        users = []

        for row in rows:
            usrID = row[0]
            userName = row[1]
            email = row[2]
            password = row[3]
            user = User(usrID,userName,email,password)
            users.append(user)

        connection.close()

        return users
    
    def userLogin(self, userName: str, password: str):
        #opens a new connetion and cursor
        connection = sqlite3.connect(self.name, check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute("Select usrName, password FROM user WHERE usrName='"+str(userName)+"' AND password='"+str(password)+"'")
        if cursor.fetchone() != None:
            print ("Log in Succesful.")
            output = True
        else:
            print("Log In Failed.")
            output = False

        connection.close()

        return output

    def accountIdInUse(self: str, randomID: str): # returns T if ID is in use

        # Open a new connection and cursor
        connection = sqlite3.connect(self.name, check_same_thread=False)
        cursor = connection.cursor()

        # Check for existing accounts with matching ID
        cursor.execute("SELECT * FROM Account WHERE accID='"+str(randomID)+"'")
        if cursor.fetchall() != None:
            output = True
        output = False

        connection.close()

        return output

    def userIdInUse(self: str, randomID: str):  # returns T if ID is in use

        # Open a new connection and cursor
        connection = sqlite3.connect(self.name, check_same_thread=False)
        cursor = connection.cursor()

        # Check for existing accounts with matching ID
        cursor.execute("SELECT * FROM User WHERE usrID='" + str(randomID) + "'")
        if cursor.fetchall() != None:
            output = True
        output = False

        connection.close()

        return output

    def withdrawFromAccount(self, accountID: str, amount: float):
        # Open a new connection and cursor
        connection = sqlite3.connect(self.name, check_same_thread=False)
        cursor = connection.cursor()

        output = []

        # Get current value of account
        cursor.execute("SELECT accValue FROM Account WHERE accID='" + str(accountID) + "'")
        result = cursor.fetchall()

        # Ensure there is a result
        if result:
            value = result[0][0] # Extract the value from the first row and first column
        else:
            output.append("Error: Withdrawal Account not found")
            return output

        # Check for errors, and return any as a list of strings to display as errors
        if float(value) < amount:
            output.append("Error Insufficient Funds")
            return output

        #if not self.accountIdInUse(str(accountID)):
        #    output.append("Error Account ID Does Not Exist")


        if not output: # (if no errors)
            # Subtract from account
            newValue = value - amount
            cursor.execute(
                "UPDATE Account SET accValue = ? WHERE accID = ?",
                (newValue, accountID)
            )
            connection.commit()

        # close connection
        connection.close()

        return output

    def depositToAccount(self, accountID: str, amount: float):
        # Open a new connection and cursor
        connection = sqlite3.connect(self.name, check_same_thread=False)
        cursor = connection.cursor()

        output = []

        # Get current value of account
        cursor.execute("SELECT accValue FROM Account WHERE accID='" + str(accountID) + "'")
        result = cursor.fetchall()

        # Ensure there is a result
        if result:
            value = result[0][0]  # Extract the value from the first row and first column
        else:
            output.append("Error: Depositing Account not found")
            return output

        # Check for errors, and return any as a list of strings to display as errors
        if float(value) < 0:
            output.append("Error Cannot Deposit Less Than Zero")
            return output

       # if not self.accountIdInUse(str(accountID)):
       #     output.append("Error Account ID Does Not Exist")


        if not output: # (if no errors)
            # Deposit to account
            newValue = value + amount
            cursor.execute(
                "UPDATE Account SET accValue = ? WHERE accID = ?",
                (newValue, accountID)
            )
            connection.commit()

        # close connection
        connection.close()

        return output
    
    def passwordReset(self, userName: str , email: str ,password: str): # lets a user reset their password in the database

        # Open a new connection and cursor
        connection = sqlite3.connect(self, check_same_thread=False)
        cursor = connection.cursor()

        # Find User's account from username and email
        cursor.execute(
            "UPDATE user set password ='" + str(password) + "' WHERE usrName='" + str(userName) + "' AND email ='" + str(email) + "'"
            )
        
        cursor.close()
        
        connection.commit()

        connection.close()

        return True
