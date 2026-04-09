from datetime import datetime

from typing import Optional

from account.enums import AccountCurrency
from bank.constants import MAX_AMOUNT_PER_OPERATION
from transaction.enums import TransactionStatus
from .base_log import BaseLog
from .enums import TransactionEntity, TransactionDirection, LogType, LogLevel, RiskLevel


class TransactionLog(BaseLog):
    def __init__(self, entity: TransactionEntity, transaction_id: str, executed_at:datetime, created_at:datetime, amount: int, direction:TransactionDirection, currency: AccountCurrency, status:TransactionStatus, account_id=None, client_id=None, risk=None, reject_reason=None):
        super().__init__(log_type=LogType.TRANSACTION)
        self.entity: TransactionEntity = entity
        self.account_id: Optional[str] = account_id
        self.client_id: Optional[str] = client_id
        self.transaction_id: str = transaction_id
        self.created_at: datetime = created_at
        self.executed_at:datetime = executed_at
        self.amount:int = amount
        self.currency: AccountCurrency = currency
        self.direction:TransactionDirection = direction
        self.status: TransactionStatus = status
        self.risk: Optional[RiskLevel] = risk
        self.reject_reason: Optional[str] = reject_reason
        self._resolve_level()

    def _resolve_level(self):
        if self.status == TransactionStatus.REJECTED:
            self.set_log_level(LogLevel.ERROR)

        elif self.amount > MAX_AMOUNT_PER_OPERATION:
            self.set_log_level(LogLevel.WARNING)

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "entity": self.entity.value,
            "account_id": self.account_id,
            "client_id": self.client_id,
            "transaction_id": self.transaction_id,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "executed_at": self.executed_at.strftime('%Y-%m-%d %H:%M:%S'),
            "amount": self.amount,
            "direction": self.direction.value,
            "status": self.status.value,
            "currency": self.currency.value,
            "risk": getattr(self.risk, "value", None),
            "reject_reason": self.reject_reason,
        }

    def get_signed_amount(self) -> int:
        if self.direction == TransactionDirection.DEBIT:
            return -self.amount
        else:
            return self.amount

    def __str__(self):
        parts = [
            f"[{self.created_at.strftime('%Y-%m-%d %H:%M:%S')}] TransactionLog",
            f"ID: {self.transaction_id}",
            f"Entity: {self.entity.name}",
            f"Direction: {self.direction.name}",
            f"Amount: {self.amount} {self.currency.name}",
            f"Status: {self.status.name}",
            f"Level: {self.log_level.name}"
        ]
        if self.account_id:
            parts.append(f"Account ID: {self.account_id}")
        if self.client_id:
            parts.append(f"Client ID: {self.client_id}")
        if self.risk:
            parts.append(f"Risk: {self.risk.name}")
        parts.append(f"Executed At: {self.executed_at.strftime('%Y-%m-%d %H:%M:%S')}")
        return " | ".join(parts)
