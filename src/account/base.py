from abc import ABC
from .enums import AccountStatus

class AccountFrozenError(Exception):
    pass

class AccountClosedError(Exception):
    pass

class InvalidOperationError(Exception):
    pass

class InsufficientFundsError(Exception):
    pass

class AbstractAccount(ABC):
    def __init__(self, owner_name: str, id: str, balance=0, status=AccountStatus.ACTIVE):
        self.id = id
        self.owner_name = owner_name
        self._balance:int = balance
        self.status = status
        
    @property
    def balance(self):
        return self._balance
    
    def _check_account_status(self):
        if self.status == AccountStatus.FROZEN:
            raise AccountFrozenError

        if self.status == AccountStatus.CLOSED:
            raise AccountClosedError

    def _check_operation_amount(self, amount):
        if amount < 0:
            raise InvalidOperationError

    def deposit(self, amount: int):
        self._check_account_status()
        self._check_operation_amount(amount)
        
        self._balance += amount

        return self.balance

    def withdraw(self, amount: int):
        self._check_account_status()
        self._check_operation_amount(amount)
        
        if self.balance < amount:
            raise InsufficientFundsError
            
        self._balance -= amount

        return self.balance

    def get_account_info(self):
        return {
            'id' : self.id,
            'owner_name' : self.owner_name,
            'status' : self.status,
            'balance' : self.balance,
        }
