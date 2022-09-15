from enum import Enum, IntEnum


class LocationCode(Enum):
    EU = 'Europe'
    US = 'United States'
    NONE = 'Undefined'


class NameStatus:
    NAME_INVALID = 1
    NAME_TAKEN = 2
    NAME_AVAILABLE = 3


class GameMap(Enum):
    MIRAGE = 'Mirage'
    CACHE = 'Cache'
    INFERNO = 'Inferno'
    NUKE = 'Nuke'
    OVERPASS = 'Overpass'
    DUST_II = 'Dust II'
    TRAIN = 'Train'
