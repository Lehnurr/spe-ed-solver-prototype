from enum import Enum


class PlayerAction(Enum):
    TURN_LEFT = 1
    TURN_RIGHT = 2
    SLOW_DOWN = 3
    SPEED_UP = 4
    CHANGE_NOTHING = 5
