import json
from datetime import datetime, timedelta
from collections import defaultdict

from .account_log import AccountLog
from .enums import RiskLevel, LogLevel, LogType
from .login_log import LoginLog
from .types import LogEntity
from .transaction_log import TransactionLog

class AuditLog:
    def __init__(self):
        self.logs: list[LogEntity] = []

    def add_log(self, log:LogEntity):
        self.logs.append(log)

    def get_exception_message(self, error: Exception) -> str:
        return f"{type(error).__name__}: {error}"

    def get_operations_per_hour_count(self, client_id: str) -> int:
        current_time = datetime.now()
        client_transactions = self.get_client_transactions(client_id)
        last_hour_transactions = [log for log in client_transactions if  (current_time - log.created_at) <= timedelta(hours=1)]
        return len(last_hour_transactions)

    def get_client_transactions(self, client_id: str) -> list[TransactionLog]:
        return  [log for log in self.logs
                if log.log_type == LogType.TRANSACTION
                and log.client_id == client_id]

    def get_suspicious_transactions(self) -> list[TransactionLog]:
        return [log for log in self.logs
                if getattr(log, "log_type", None) == LogType.TRANSACTION
                and (getattr(log, "risk", None) == RiskLevel.HIGH
                or getattr(log, "risk", None) == RiskLevel.MEDIUM
                or log.log_level != LogLevel.INFO)]

    def get_client_risk_profile(self, client_id: str) -> dict[RiskLevel, int]:
        client_transactions = self.get_client_transactions(client_id)

        result = defaultdict(int)

        for log in client_transactions:
            if getattr(log, "risk", None) is None:
                continue

            result[log.risk] +=1

        return result

    def get_errors(self) -> list[LogEntity]:
        return [log for log in self.logs if log.log_level == LogLevel.ERROR]

    def get_all_transaction_logs(self) -> list[TransactionLog]:
        return [log for log in self.logs
                if log.log_type == LogType.TRANSACTION]

    def get_all_login_logs(self) -> list[LoginLog]:
        return [log for log in self.logs
                if log.log_type == LogType.LOGIN]

    def get_all_account_logs(self) -> list[AccountLog]:
        return [log for log in self.logs
                if log.log_type == LogType.ACCOUNT]

    def save_logs_to_json_file(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump([log.to_dict() for log in self.logs], f, indent=4)