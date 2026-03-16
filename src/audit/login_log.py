from datetime import datetime

from typing import Optional

from .enums import  LogType, LoginStatus
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
