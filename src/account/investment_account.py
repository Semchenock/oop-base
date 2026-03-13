from .bank_account import BankAccount
from .enums import AssetType


class Asset:
    def __init__(self, asset_type:AssetType, name:str, price:int, yearly_interest:int=0):
        self.asset_type:AssetType = asset_type
        self.name:str = name
        self.price:int = price
        self.yearly_interest:int = yearly_interest

    def __repr__(self):
        return f"{self.name}({self.asset_type}, price={self.price}, interest={self.yearly_interest}%)"


class InvestmentAccount(BankAccount):
    def __init__(self, assets, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assets:list[Asset] = assets

    def project_yearly_growth(self):
        yearly_growth = sum(asset.price * (asset.yearly_interest / 100) for asset in self.assets)
        return yearly_growth

    def get_account_info(self):
        return {**super().get_account_info(),
                **{'assets': self.assets}}

    def __str__(self):
        return (f"{super().__str__()} |"
                f"Assets: {self.assets}"
        )