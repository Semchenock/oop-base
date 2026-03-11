from enum import Enum

class AccountStatus(Enum):
    ACTIVE = 'active'
    FROZEN = 'frozen'
    CLOSED = 'closed'

class AccountCurrency(Enum):
    RUB = 'RUB'
    USD = 'USD'
    EUR = 'EUR'
    KZT = 'KZT'
    CNY = 'CNY'

class AssetType(Enum):
    STOCK = 'stock'
    ETF = 'etf'
    BOND = 'bonds'