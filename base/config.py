from enum import Enum

class TraceLevels(Enum):
    ERROR = 1
    WARN = 2
    INFO = 3
    DEBUG = 4


platform_name = 'eusebio'

trace_level = TraceLevels.DEBUG.value

