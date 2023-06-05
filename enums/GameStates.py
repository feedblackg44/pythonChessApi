from enum import Enum


class GameStates(Enum):
    PROMOTION = -1
    NORMAL = 0
    CHECK = 1
    MATE = 2
    TIE = 3
