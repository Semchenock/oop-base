from abc import ABC

from .enums import LogLevel, LogType


class BaseLog(ABC):
    def __init__(self, log_type: LogType):
        self.log_level: LogLevel = LogLevel.INFO
        self.log_type:LogType = log_type

    def set_log_level(self, log_level: LogLevel = LogLevel.INFO):
        self.log_level = log_level