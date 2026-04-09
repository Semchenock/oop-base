from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

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
    def __init__(self, owner_name: str, id: str, client_id: Optional[str] = None, status=AccountStatus.ACTIVE):
        self.id:str = id
        self.client_id:Optional[str] = client_id
        self.owner_name:str = owner_name
        self._balance:int = 0
        self.status:AccountStatus = status
        self.created_at:datetime = datetime.now()
        
    @property
    def balance(self):
        return self._balance

    def _check_account_status(self):
        if self.status == AccountStatus.FROZEN:
            raise AccountFrozenError

        if self.status == AccountStatus.CLOSED:
            raise AccountClosedError

    def _check_operation_amount_type(self, amount:int):
        if not isinstance(amount, int) or isinstance(amount, bool):
            raise InvalidOperationError(f"Invalid type for amount: {type(amount).__name__}")

    def _check_operation_amount(self, amount:int):
        if amount < 0:
            raise InvalidOperationError

    def _check_withdraw_allowed(self, amount:int):
        if self.balance < amount:
            raise InsufficientFundsError

    @abstractmethod
    def deposit(self, amount:int) -> int:
        self._check_account_status()
        self._check_operation_amount_type(amount)
        self._check_operation_amount(amount)
        
        self._balance += amount

        return self.balance

    def _run_withdraw_checks(self, amount:int):
        self._check_account_status()
        self._check_operation_amount_type(amount)
        self._check_operation_amount(amount)
        self._check_withdraw_allowed(amount)

    @abstractmethod
    def withdraw(self, amount:int) -> int:
        self._run_withdraw_checks(amount)
            
        self._balance -= amount

        return self.balance

    @abstractmethod
    def get_account_info(self):
        return {
            'id' : self.id,
            'owner_name' : self.owner_name,
            'status' : self.status.value,
            'balance' : self.balance,
        }

    def close_account(self):
        self.status = AccountStatus.CLOSED

    def freeze_account(self):
        self.status = AccountStatus.FROZEN

    def unfreeze_account(self):
        self.status = AccountStatus.ACTIVE

    def add_client_id(self, client_id:str):
        self.client_id = client_id