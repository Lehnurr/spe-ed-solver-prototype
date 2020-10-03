import json
from enum import Enum


class PlayerAction(Enum):
    TURN_LEFT = 1
    TURN_RIGHT = 2
    SLOW_DOWN = 3
    SPEED_UP = 4
    CHANGE_NOTHING = 5


class PlayerDirection(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4

    def turn(self, action: PlayerAction):
        new_value = self.value
        if action == PlayerAction.TURN_LEFT:
            new_value -= 1
            if new_value == 0:
                new_value = PlayerDirection.LEFT.value
        elif action == PlayerAction.TURN_RIGHT:
            new_value += 1
            if new_value == 5:
                new_value = PlayerDirection.UP.value
        return PlayerDirection(new_value)


class Player(object):
    def __init__(self, player_id: int, x_position: int, y_position: int):
        self.player_id = player_id
        self.position = [x_position, y_position]
        self.speed = 1
        self.next_action = None
        self.direction = PlayerDirection.LEFT

    def to_json(self):
        return json.dumps(
            {
                self.player_id:
                    {
                        "x": self.position[0],
                        "y": self.position[1],
                        "direction": self.direction.name.lower(),
                        "speed": self.speed,
                        "active": self.speed > 0,
                        "name": f'Player #{self.player_id}'
                    }
            }
        )
