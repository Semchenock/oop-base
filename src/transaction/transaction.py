import uuid
from datetime import datetime
from typing import Optional

from .enums import TransactionStatus
from account.types import AccountType
from account.enums import AccountCurrency
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

    def execute(self, bank:Bank):
        deposit_amount = self.amount * round((100 - self.commission) / 100)
        converted_deposit_amount = bank.convert_currency(deposit_amount, self.from_account.currency, self.to_account.currency)

        try:
            self.from_account.withdraw(self.amount)
            self.to_account.deposit(converted_deposit_amount)
        except Exception as e:
            self.reject_reason = e
            self.status = TransactionStatus.REJECTED
            return

        self.status = TransactionStatus.EXECUTED



