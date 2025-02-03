from Account import *
class Savings(Account):
    def __init__(self, accountNumber: str, balance: float, interestRate: float):
        super().__init__(accountNumber, "Savings", balance)
        self.interestRate = interestRate

    def printAccountDetails(self):
        super().printAccountDetails()
        print(f"Interest Rate: {self.interestRate:.2%}")