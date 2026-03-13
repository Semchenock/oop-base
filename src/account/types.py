
from .bank_account import BankAccount
from .premium_account import PremiumAccount
from .savings_account import SavingsAccount
from .investment_account import InvestmentAccount

AccountType = BankAccount | PremiumAccount | SavingsAccount | InvestmentAccount