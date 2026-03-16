from datetime import datetime

from typing import Optional

from account.enums import AccountCurrency
from bank.bank import MAX_AMOUNT_PER_OPERATION
from transaction.enums import TransactionStatus
from .base_log import BaseLog
from .enums import TransactionEntity, TransactionDirection, LogType, LogLevel

class TransactionLog(BaseLog):
    def __init__(self, entity: TransactionEntity, transaction_id: str, executed_at:datetime, amount: int, direction:TransactionDirection, currency: AccountCurrency, status:TransactionStatus, account_id=None, client_id=None):
        super().__init__(log_type=LogType.TRANSACTION)
        self.entity: TransactionEntity = entity
        self.account_id: Optional[str] = account_id
        self.client_id: Optional[str] = client_id
        self.transaction_id: str = transaction_id
        self.executed_at:datetime = executed_at
        self.amount:int = amount
        self.currency: AccountCurrency = currency
        self.direction:TransactionDirection = direction
        self.status: TransactionStatus = status
        self._resolve_level()

    def _resolve_level(self):
        if self.status == TransactionStatus.REJECTED:
            self.set_log_level(LogLevel.ERROR)

        elif self.amount > MAX_AMOUNT_PER_OPERATION:
            self.set_log_level(LogLevel.WARNING)
