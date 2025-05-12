class AuditLog:
    def __init__(self, ID : int, Operation : str, TableName : str, oldValue : str, newValue : str, ChangedAt : str, signature: str):
        self.ID = ID
        self.Operation = Operation
        self.TableName = TableName
        self.oldValue = oldValue
        self.newValue = newValue
        self.ChangedAt = ChangedAt
        self.signature = signature