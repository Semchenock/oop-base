from enum import Enum


class LogType(Enum):
    TRANSACTION = 'TRANSACTION'
    LOGIN = 'LOGIN'
    ACCOUNT = 'ACCOUNT'

class LogLevel(Enum):
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'

class TransactionEntity(Enum):
    CLIENT = "CLIENT"
    EXTERNAL = "EXTERNAL"

class TransactionDirection(Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

class AccountActionsEnum(Enum):
    CREATE = "CREATE"
    FREEZE = "FREEZE"
    UNFREEZE = "UNFREEZE"
    CLOSE = "CLOSE"

class LoginStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"