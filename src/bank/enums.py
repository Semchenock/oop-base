from enum import Enum

class ClientAccountStatus(Enum):
    ACTIVE = 'active'
    FROZEN = 'frozen'
    CLOSED = 'closed'

class FraudType(Enum):
    NIGHT_OPERATION = 'NIGHT_OPERATION'
    LOGIN_FAILED = 'LOGIN_FAILED'
    BIG_TRANSACTION = 'BIG_TRANSACTION'
    TOO_MANY_SESSIONS = 'TOO_MANY_SESSIONS'