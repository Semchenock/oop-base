from .bank_account import BankAccount
from .base import InsufficientFundsError

class SavingsAccount(BankAccount):
    def __init__(self, min_balance=0, monthly_interest=0, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.min_balance=min_balance
        self.monthly_interest=monthly_interest

    def withdraw(self, amount):
        if amount > self.balance - self.min_balance:
            raise InsufficientFundsError()

        return super().withdraw(amount)
    
    def apply_monthly_interest(self):
        interest:int = round(self.balance*(self.monthly_interest/100))
        self.deposit(interest)

    def get_account_info(self):
        return {**super().get_account_info(), **{'min_balance': self.min_balance, 'monthly_interest': self.monthly_interest}}

    def __str__(self):
        return (f"{super().__str__()} |"
                f"Min balance: {self.min_balance} | "
                f"Monthly interest: {self.monthly_interest}%"
        )