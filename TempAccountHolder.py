from Account import *
class AccountHolder:
    contents = []
    accountNumber = 0
    def __init__(self):
        self.contents.append(Account(1,'Savings',32.0))
        self.contents.append(Account(2, 'Checking', 350.0))
        self.contents.append(Account(3, 'Investment', 50000000.0))

    def addAccount(self, accountName: str, balance: float):
        self.accountNumber = self.accountNumber + 1
        self.contents.append(Account(self.accountNumber, accountName, balance))