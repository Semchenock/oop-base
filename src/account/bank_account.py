import uuid
from typing import Optional

from .base import AbstractAccount
from .enums import AccountCurrency

class BankAccount(AbstractAccount):
    def __init__(self,  id:Optional[str]=None, currency:AccountCurrency=AccountCurrency.RUB, *args, **kwargs):
        if id is None:
            self.id = uuid.uuid4().hex[:8]
        
        super().__init__(id=self.id, *args, **kwargs)
        self.currency:AccountCurrency = currency

    def get_account_info(self):
        return {**super().get_account_info(), **{'currency' : self.currency.value}}

    def withdraw(self, amount: int) -> int:
        return super().withdraw(amount)

    def deposit(self, amount: int) -> int:
        return super().deposit(amount)

    def __str__(self):
         return (
            f"{self.__class__.__name__} | "
            f"Owner: {self.owner_name} | "
            f"Account: ****{self.id[-4:]} | "
            f"Status: {self.status.value} | "
            f"Balance: {self.balance} {self.currency.value}"
        )