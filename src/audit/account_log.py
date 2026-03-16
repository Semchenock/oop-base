from datetime import datetime

from .enums import AccountActionsEnum, LogType, LogLevel
from .base_log import BaseLog

class AccountLog(BaseLog):
    def __init__(self, account_id:str, action: AccountActionsEnum):
        super().__init__(log_type=LogType.ACCOUNT)
        self.account_id = account_id
        self.action = action
        self.created_at = datetime.now()
        self._resolve_level()

    def _resolve_level(self):
        if self.action == AccountActionsEnum.FREEZE:
            self.set_log_level(LogLevel.ERROR)

        elif self.action == AccountActionsEnum.CLOSE:
            self.set_log_level(LogLevel.WARNING)
