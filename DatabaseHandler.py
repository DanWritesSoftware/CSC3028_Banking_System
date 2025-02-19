import sqlite3
from Account import Account

from User import User

class Database:
    def __init__(self, name):
        self.name = name
        # connection and cursor are now locally opened and closed with each class function
        #self.connection = sqlite3.connect(name, check_same_thread=False)
        #self.cursor = self.connection.cursor()

    def createAccount(self, accID, usrID, accName, accBalance):
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
    
    def createUser(self, usrID, usrName, email, password):
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

    def getUserAccounts(self, usrID):
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
    
    def getUsers(self, usrID):
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
    
    def userLogin(self, userName, password):
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

    def accountIdInUse(self, randomID): # returns T if ID is in use

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