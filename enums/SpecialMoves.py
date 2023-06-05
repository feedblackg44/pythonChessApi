from enum import Enum


class SpecialMoves(Enum):
    PROMOTE = -1
    NORMAL = 0
    SHORT_CASTLE = 1
    LONG_CASTLE = 2
    EN_PASSANT = 3
