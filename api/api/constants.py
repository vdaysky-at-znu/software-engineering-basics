from enum import Enum, IntEnum
from typing import Type


class LocationCode(Enum):
    EU = 'Europe'
    US = 'United States'
    NONE = 'Undefined'


class NameStatus:
    NAME_INVALID = 1
    NAME_TAKEN = 2
    NAME_AVAILABLE = 3


AVAILABLE_PUBS_THRESHOLD = 2
