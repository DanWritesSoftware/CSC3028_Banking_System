import sqlite3
from Account import Account

class Database:
    def __init__(self, name):
        self.name = name
        # connection and cursor are now locally opened and closed with each class function
        #self.connection = sqlite3.connect(name, check_same_thread=False)
        #self.cursor = self.connection.cursor()

    def createAccount(self, usrID, accName, accBalance):
        # Open a new connection and cursor
        connection = sqlite3.connect(self.name, check_same_thread=False)
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO Account (accType, accUserID, accValue) VALUES (?, ?, ?)",
            (accName, usrID, accBalance)
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