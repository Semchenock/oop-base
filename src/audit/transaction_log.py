from datetime import datetime

from typing import Optional

from account.enums import AccountCurrency
from transaction.enums import TransactionStatus
from .base_log import BaseLog
from .enums import TransactionEntity, TransactionDirection, LogType

class TransactionLog(BaseLog):
    def __init__(self, entity: TransactionEntity, transaction_id: str, executed_at:datetime, amount: int, direction:TransactionDirection, currency: AccountCurrency, status:TransactionStatus, account_id=None, client_id=None):
        super().__init__()
        self.entity: TransactionEntity = entity
        self.account_id: Optional[str] = account_id
        self.client_id: Optional[str] = client_id
        self.transaction_id: str = transaction_id
        self.executed_at:datetime = executed_at
        self.amount:int = amount
        self.currency: AccountCurrency = currency
        self.direction:TransactionDirection = direction
        self.status: TransactionStatus = status
        self.type = LogType.TRANSACTION