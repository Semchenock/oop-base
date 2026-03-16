from .types import LogEntity


class AuditLog:
    def __init__(self):
        self.logs: list[LogEntity] = []

    def add_log(self, log:LogEntity):
        self.logs.append(log)