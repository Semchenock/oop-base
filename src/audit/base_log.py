from abc import ABC

from .enums import LogLevel, LogType
from .constants import LOG_LEVEL_ORDER

class BaseLog(ABC):
    def __init__(self, log_type: LogType):
        self.log_level: LogLevel = LogLevel.INFO
        self.log_type:LogType = log_type

    def set_log_level(self, log_level: LogLevel = LogLevel.INFO):
        current_level_index = LOG_LEVEL_ORDER.index(self.log_level)
        new_log_level_index = LOG_LEVEL_ORDER.index(log_level)

        if new_log_level_index > current_level_index:
            self.log_level = log_level