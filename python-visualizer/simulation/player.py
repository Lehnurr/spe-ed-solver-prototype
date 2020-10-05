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
    def __init__(self, player_id: int, x_position: int, y_position: int,
                 speed: int = 1, direction: PlayerDirection = PlayerDirection.LEFT):
        self.player_id = player_id
        self.position = [x_position, y_position]
        self.speed = speed
        self.next_action = None
        self.direction = direction

    # returns all passed cells (including jumped over cells)
    def do_action(self) -> [(int, int)]:
        # Apply next_action
        if (self.speed == 0 or
                self.next_action is None or
                (self.next_action == PlayerAction.SLOW_DOWN and self.speed == 1) or
                (self.next_action == PlayerAction.SPEED_UP and self.speed == 10)):
            self.speed = 0
            self.next_action = None
            return []
        elif self.next_action == PlayerAction.TURN_LEFT or self.next_action == PlayerAction.TURN_RIGHT:
            self.direction = self.direction.turn(self.next_action)
        elif self.next_action == PlayerAction.SLOW_DOWN:
            self.speed -= 1
        elif self.next_action == PlayerAction.SPEED_UP:
            self.speed += 1

        new_position = self.position.copy()
        passed_cells = []

        # Move and calculate the passed Cells
        if self.direction == PlayerDirection.UP:
            new_position[1] = self.position[1] - self.speed
            for pos in range(new_position[1], self.position[1]):
                passed_cells.append((self.position[0], pos))
        elif self.direction == PlayerDirection.RIGHT:
            new_position[0] = self.position[0] + self.speed
            for pos in range(self.position[0] + 1, new_position[0] + 1):
                passed_cells.append((pos, self.position[1]))
        elif self.direction == PlayerDirection.DOWN:
            new_position[1] = self.position[1] + self.speed
            for pos in range(self.position[1] + 1, new_position[1] + 1):
                passed_cells.append((self.position[0], pos))
        elif self.direction == PlayerDirection.LEFT:
            new_position[0] = self.position[0] - self.speed
            for pos in range(new_position[0], self.position[0]):
                passed_cells.append((pos, self.position[1]))

        # Apply move on Player
        self.next_action = None
        self.position = new_position
        return passed_cells

    def to_dict(self):
        return {
            "x": self.position[0],
            "y": self.position[1],
            "direction": self.direction.name.lower(),
            "speed": self.speed,
            "active": self.speed > 0,
            "name": f'Player #{self.player_id}'
        }

    def copy(self):
        return Player(self.player_id, self.position[0], self.position[1], self.speed, self.direction)
