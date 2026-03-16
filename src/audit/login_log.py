from datetime import datetime

from typing import Optional

from bank.client import MAX_TRY_COUNT
from .enums import  LogType, LoginStatus, LogLevel
from .base_log import BaseLog

class LoginLog(BaseLog):
    def __init__(self, status: LoginStatus, client_id: str, session_id: Optional[str] = None, sessions_count: Optional[int] = None, try_count: int = 0):
        super().__init__(log_type=LogType.LOGIN)
        self.client_id: Optional[str] = client_id
        self.created_at = datetime.now()
        self.status: LoginStatus = status
        self.try_count: int = try_count
        self.session_id: Optional[str] = session_id
        self.sessions_count: Optional[int] = sessions_count
        self._resolve_level()

    def _resolve_level(self):
        if self.try_count >= MAX_TRY_COUNT:
            self.set_log_level(LogLevel.ERROR)
        elif self.status == LoginStatus.FAILED:
            self.set_log_level(LogLevel.WARNING)
