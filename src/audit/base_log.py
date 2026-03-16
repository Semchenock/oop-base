from abc import ABC

from audit.enums import LogLevel


class BaseLog(ABC):
    def __init__(self):
        self.log_level: LogLevel = LogLevel.INFO

    def set_log_level(self, log_level: LogLevel = LogLevel.INFO):
        self.log_level = log_level