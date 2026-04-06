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

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "client_id": self.client_id,
            "status": self.status.value,
            "try_count": self.try_count,
            "session_id": self.session_id,
            "sessions_count": self.sessions_count,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def __str__(self):
        session_info = f" | Session: {self.session_id}" if self.session_id else ""
        sessions_count_info = f" | Active Sessions: {self.sessions_count}" if self.sessions_count is not None else ""
        return (
            f"[{self.created_at.strftime('%Y-%m-%d %H:%M:%S')}] "
            f"LoginLog | Client ID: {self.client_id} | "
            f"Status: {self.status.name} | "
            f"Try Count: {self.try_count}{session_info}{sessions_count_info} | "
            f"Level: {self.log_level.name}"
        )