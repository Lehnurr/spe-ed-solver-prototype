from enum import Enum


class PlayerAction(Enum):
    TURN_LEFT = 1,
    TURN_RIGHT = 2,
    SLOW_DOWN = 3,
    SPEED_UP = 4,
    CHANGE_NOTHING = 5


class PlayerDirection(Enum):
    UP = 1,
    RIGHT = 2,
    DOWN = 3,
    LEFT = 4


class Player(object):
    def __init__(self, player_id: int, x_position: int, y_position: int):
        self.player_id = player_id
        self.x_position = x_position
        self.y_position = y_position
        self.speed = 1
        self.next_action = None
        self.direction = PlayerDirection.UP
