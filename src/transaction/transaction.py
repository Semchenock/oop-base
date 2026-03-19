from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from .enums import TransactionStatus
from account.types import AccountType
from account.enums import AccountCurrency
from audit.transaction_log import TransactionLog
from audit.enums import TransactionEntity, TransactionDirection, RiskLevel
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

    def cancel(self, reason: str = None, bank=None):
        self.status = TransactionStatus.CANCELED

        if bank is not None:
            log = self._create_log(
                status=TransactionStatus.CANCELED,
                amount=self.amount,
                direction=TransactionDirection.DEBIT,
                account=self.from_account,
                risk=RiskLevel.HIGH,
                created_at=self.timestamp,
            )

            bank.audit_log.add_log(log)

    def can_execute(self) -> bool:
        is_executable_status:bool = self.status == TransactionStatus.CREATED
        is_executable_time: bool = self.execute_time is None or self.execute_time < datetime.now()

        return is_executable_status and is_executable_time

    def _create_log(self, amount: int, direction: TransactionDirection, account: AccountType, status: TransactionStatus, risk: RiskLevel, created_at:datetime) -> TransactionLog:
        return TransactionLog(
            entity=TransactionEntity.CLIENT,
            transaction_id=self.transaction_id,
            executed_at=datetime.now(),
            created_at=created_at,
            amount=amount,
            direction=direction,
            client_id=account.client_id,
            account_id=account.id,
            currency=account.currency,
            status=status,
            risk=risk
        )

    def execute(self, bank: Bank):
        deposit_amount = round(self.amount * (100 - self.commission) / 100)
        converted_deposit_amount = bank.convert_currency(
            deposit_amount,
            self.from_account.currency,
            self.to_account.currency
        )

        client = bank.search_client_by_account_id(self.from_account.id)

        if client is None:
            self.cancel()
            return

        risk = bank.risk_analyzer.analyze_transaction(transaction=self, client=client)

        if risk == RiskLevel.HIGH:
            self.cancel(reason='High risk', bank=bank)
            return

        withdraw_log_args = {
            'amount': self.amount,
            'direction': TransactionDirection.DEBIT,
            'account': self.from_account,
            'risk': risk,
            'created_at': self.timestamp,
        }

        deposit_log_args = {
            'amount': converted_deposit_amount,
            'direction': TransactionDirection.CREDIT,
            'account': self.to_account,
            'risk': risk,
            'created_at': self.timestamp,
        }

        try:
            self.from_account.withdraw(self.amount)

            log = self._create_log(status=TransactionStatus.EXECUTED, **withdraw_log_args)
            bank.audit_log.add_log(log)

        except Exception as e:
            self.reject_reason = e
            self.status = TransactionStatus.REJECTED

            log = self._create_log(status=TransactionStatus.REJECTED, **withdraw_log_args)
            bank.audit_log.add_log(log)

            return

        try:
            self.to_account.deposit(converted_deposit_amount)

            log = self._create_log(status=TransactionStatus.EXECUTED, **deposit_log_args)
            bank.audit_log.add_log(log)

        except Exception as e:
            self.reject_reason = e
            self.status = TransactionStatus.REJECTED

            log = self._create_log(status=TransactionStatus.REJECTED, **deposit_log_args)
            bank.audit_log.add_log(log)

            try:
                self.from_account.deposit(self.amount)

                rollback_log = self._create_log(
                    status=TransactionStatus.EXECUTED,
                    amount=self.amount,
                    direction=TransactionDirection.CREDIT,
                    account=self.from_account,
                    risk=RiskLevel.HIGH,
                    created_at=self.timestamp,
                )
                bank.audit_log.add_log(rollback_log)

            except Exception as rollback_error:
                critical_log = self._create_log(
                    status=TransactionStatus.REJECTED,
                    amount=self.amount,
                    direction=TransactionDirection.CREDIT,
                    account=self.from_account,
                    risk=RiskLevel.CRITICAL,
                    created_at=self.timestamp,
                )
                bank.audit_log.add_log(critical_log)

            return

        self.status = TransactionStatus.EXECUTED


