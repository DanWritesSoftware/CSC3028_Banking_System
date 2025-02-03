from Account import *
class Investing(Account):
    def __init__(self, accountNumber: str, balance: float):
        super().__init__(accountNumber, "Investing", balance)