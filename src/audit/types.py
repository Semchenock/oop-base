from .transaction_log import TransactionLog
from .account_log import AccountLog
from .login_log import LoginLog

LogEntity = TransactionLog | AccountLog | LoginLog