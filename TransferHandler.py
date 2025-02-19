from DatabaseHandler import Database

class Transfer:
    def __init__(self, fromID:str, toID:str, transferAmount:float, database):
        self.fromID = fromID
        self.toID = toID
        self.transferAmount = transferAmount
        self.database = database
    def tryTransfer(self):
        # will return errors as string array
        output = []
        withdrawErrors = []
        depositErrors = []

        withdrawErrors = self.database.withdrawFromAccount(self.fromID, self.transferAmount)

        if not withdrawErrors:
            depositErrors = self.database.depositToAccount(self.toID, self.transferAmount)

        if not withdrawErrors and not depositErrors:
            return []
        else:
            for error in withdrawErrors:
                output.append(error)
            for error in depositErrors:
                output.append(error)

        return output