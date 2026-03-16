from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from .enums import TransactionStatus
from account.types import AccountType
from account.enums import AccountCurrency
from audit.transaction_log import TransactionLog
from audit.enums import TransactionEntity, TransactionDirection
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bank.bank import Bank

class Transaction:
    def __init__(self, amount:int, currency:AccountCurrency, commission:int, from_account:AccountType, to_account:AccountType, priority:int=0, execute_time:datetime=None):
        self.amount:int = amount
        self.currency:AccountCurrency = currency
        self.commission:int = commission
        self.from_account:AccountType = from_account
        self.to_account:AccountType = to_account
        self.priority:int = priority
        self.status:TransactionStatus = TransactionStatus.CREATED
        self.reject_reason:Optional[Exception] = None
        self.timestamp:datetime = datetime.now()
        self.transaction_id:str = str(uuid.uuid4())
        self.execute_time:Optional[datetime] = execute_time

    def cancel(self):
        self.status = TransactionStatus.CANCELED

    def can_execute(self) -> bool:
        is_executable_status:bool = self.status == TransactionStatus.CREATED
        is_executable_time: bool = self.execute_time is None or self.execute_time < datetime.now()

        return is_executable_status and is_executable_time

    def _create_log(self, amount: int, direction: TransactionDirection, account: AccountType, status: TransactionStatus) -> TransactionLog:
        return TransactionLog(
            entity=TransactionEntity.CLIENT,
            transaction_id=self.transaction_id,
            executed_at=datetime.now(),
            amount=amount,
            direction=direction,
            client_id=account.client_id,
            account_id=account.id,
            currency=account.currency,
            status=status,
        )

    def execute(self, bank:Bank):
        deposit_amount = round(self.amount * (100 - self.commission) / 100)
        converted_deposit_amount = bank.convert_currency(deposit_amount, self.from_account.currency, self.to_account.currency)

        withdraw_log_args = {
            'amount': self.amount,
            'direction': TransactionDirection.DEBIT,
            'account': self.from_account
        }

        deposit_log_args = {
            'amount': converted_deposit_amount,
            'direction': TransactionDirection.CREDIT,
            'account': self.to_account,
        }


        try:
            self.from_account.withdraw(self.amount)

            log = self._create_log(status = TransactionStatus.EXECUTED, **withdraw_log_args)
            bank.audit_log.add_log(log)
        except Exception as e:
            self.reject_reason = e
            self.status = TransactionStatus.REJECTED
            log = self._create_log(status=TransactionStatus.REJECTED, **withdraw_log_args)
            bank.audit_log.add_log(log)
            return

        try:
            self.to_account.deposit(converted_deposit_amount)
            log = self._create_log(status = TransactionStatus.EXECUTED, **deposit_log_args)
            bank.audit_log.add_log(log)
        except Exception as e:
            self.reject_reason = e
            self.status = TransactionStatus.REJECTED
            log = self._create_log(status=TransactionStatus.REJECTED, **deposit_log_args)
            bank.audit_log.add_log(log)
            return

        self.status = TransactionStatus.EXECUTED



