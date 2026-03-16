from .types import LogEntity
from .enums import LogType, LogLevel
from transaction.enums import TransactionStatus


class AuditLog:
    def __init__(self):
        self.logs: list[LogEntity] = []

    def add_log(self, log:LogEntity):
        self.logs.append(log)