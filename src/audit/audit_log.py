from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional

from .enums import RiskLevel, LogLevel, LogType
from .types import LogEntity
from .constants import LOG_LEVEL_ORDER

class AuditLog:
    def __init__(self):
        self.logs: list[LogEntity] = []

    def add_log(self, log:LogEntity):
        self.logs.append(log)

    def get_operations_per_hour_count(self, client_id: str) -> int:
        current_time = datetime.now()
        client_transactions = self.get_client_transactions(client_id)
        last_hour_transactions = [log for log in client_transactions if  (current_time - log.created_at) <= timedelta(hours=1)]
        return len(last_hour_transactions)

    def get_client_transactions(self, client_id: str) -> list[LogEntity]:
        return  [log for log in self.logs
                if log.log_type == LogType.TRANSACTION
                and log.client_id == client_id]

    def get_suspicious_transactions(self) -> list[LogEntity]:
        return [log for log in self.logs
                if  getattr(log, "risk", None) == RiskLevel.HIGH
                or getattr(log, "risk", None) == RiskLevel.MEDIUM
                or log.log_level != LogLevel.INFO]

    def get_client_risk_profile(self, client_id: str):
        client_transactions = self.get_client_transactions(client_id)

        result = defaultdict(int)

        for log in client_transactions:
            if getattr(log, "risk", None):
                continue

            result[log.risk] +=1

    def get_errors(self) -> list[LogEntity]:
        return [log for log in self.logs if log.log_level == LogLevel.ERROR]
