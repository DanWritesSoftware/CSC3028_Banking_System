class User:
    def __init__(self, usrID: str, usrName:str , email:str , password: str):
        self.usrName = usrName
        self.password = password
        self.usrID = usrID
        self.email = email
    
    def printUserDetails(self):
        print(f"User Name: {self.usrName} , Password: {self.password}" )