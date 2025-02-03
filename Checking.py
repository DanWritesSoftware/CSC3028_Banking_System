from Account import *
class Checking(Account):
    def __init__(self, accountNumber: str, balance: float):
        super().__init__(accountNumber, "Checking", balance)