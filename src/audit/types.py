from .transaction_log import TransactionLog
from .account_log import AccountLog

LogEntity = TransactionLog | AccountLog