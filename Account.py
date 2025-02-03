
class Account:
    def __init__(self, accountNumber: str, accountType: str, balance: float):
        self.accountNumber = accountNumber
        self.type = accountType
        self.balance = balance

    def printAccountDetails(self):
        print(f"Account Number: {self.accountNumber}, Type: {self.type}, Balance: ${self.balance:.2f}")

    def deposit(self):
        amount = float(input("Enter the amount to deposit: "))
        if amount > 0:
            self.balance += amount
            print(f"Deposit successful. New Balance: ${self.balance:.2f}")
        else:
            print("Invalid deposit amount.")

    def withdraw(self):
        amount = float(input("Enter the amount to withdraw: "))
        if amount > 0 and amount <= self.balance:
            self.balance -= amount
            print(f"Withdrawal successful. New Balance: ${self.balance:.2f}")
        else:
            print("Insufficient balance or invalid amount.")