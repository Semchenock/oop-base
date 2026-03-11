import uuid
from .base import AbstractAccount
from .enums import AccountCurrency

class BankAccount(AbstractAccount):
    def __init__(self,  id=None, currency=AccountCurrency.RUB, *args, **kwargs):
        if id is None:
            id = str(uuid.uuid4())
        
        super().__init__(id=id, *args, **kwargs)
        self.currency:AccountCurrency = currency

    def get_account_info(self):
        return {**super().get_account_info(), **{'currency' : self.currency.value}}

    def __str__(self):
         return (
            f"{self.__class__.__name__} | "
            f"Owner: {self.owner_name} | "
            f"Account: ****{self.id[-4:]} | "
            f"Status: {self.status.value} | "
            f"Balance: {self.balance} {self.currency.value}"
        )