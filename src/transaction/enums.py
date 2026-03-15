from enum import Enum

class TransactionStatus(Enum):
    CREATED = "CREATED"
    EXECUTED = "EXECUTED"
    REJECTED = "REJECTED"
    CANCELED = "CANCELED"
