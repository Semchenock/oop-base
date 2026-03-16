from .types import LogEntity
from .enums import LogType, LogLevel
from transaction.enums import TransactionStatus


class AuditLog:
    def __init__(self):
        self.logs: list[LogEntity] = []

    def add_log(self, log:LogEntity):
        if log.log_type == LogType.TRANSACTION and log.status == TransactionStatus.REJECTED:
            log.set_log_level(LogLevel.ERROR)

        self.logs.append(log)