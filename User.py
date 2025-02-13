class User:
    def __init__(self, usrID, usrName:str , password: str):
        self.usrName = usrName
        self.passWord = password
        self.usrID = usrID
    
    def printUserDetails(self):
        print(f"User Name: {self.usrName} , Password: {self.password}" )