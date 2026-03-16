from datetime import datetime

from .enums import AccountActionsEnum, LogType
from .base_log import BaseLog

class AccountLog(BaseLog):
    def __init__(self, account_id:str, action: AccountActionsEnum):
        super().__init__(log_type=LogType.ACCOUNT)
        self.account_id = account_id
        self.action = action
        self.created_at = datetime.now()