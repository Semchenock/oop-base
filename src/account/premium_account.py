from .bank_account import BankAccount
from .base import InsufficientFundsError


class PremiumAccount(BankAccount):
    def __init__(self, fee=0, overdraft_limit=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fee:int = fee
        self.overdraft_limit:int = overdraft_limit

    def _check_withdraw_allowed(self, amount):
        if amount > self.balance + self.overdraft_limit:
            raise InsufficientFundsError()

    def withdraw(self, amount:int):
        super()._run_withdraw_checks(amount)
        return super().withdraw(amount + self.fee)

    def get_account_info(self):
        return {**super().get_account_info(),
                **{'fee': self.fee, 'overdraft_limit': self.overdraft_limit}}

    def __str__(self):
        return (f"{super().__str__()} |"
                f"Fee: {self.fee} | "
                f"Overdraft limit: {self.overdraft_limit}"
        )