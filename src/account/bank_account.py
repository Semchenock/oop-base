import uuid
from .base import AbstractAccount
from .base import AccountFrozenError, AccountClosedError, InvalidOperationError, InsufficientFundsError
from .enums import AccountStatus, AccountCurrency

class BankAccount(AbstractAccount):
    def __init__(self, owner_name, status=AccountStatus.ACTIVE, id=None, balance=0,  currency=AccountCurrency.RUB):
        if id is None:
            id = str(uuid.uuid4())[:8]
        
        super().__init__(owner_name, id, balance, status)
        self.currency = currency

    def __str__(self):
         return (
            f"{self.__class__.__name__} | "
            f"Owner: {self.owner_name} | "
            f"Account: ****{self.id[-4:]} | "
            f"Status: {self.status.value} | "
            f"Balance: {self.balance} {self.currency.value}"
        )