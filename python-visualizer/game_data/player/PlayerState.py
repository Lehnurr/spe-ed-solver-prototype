from enum import Enum
from typing import Tuple

from game_data.game.Board import Board
from game_data.player.PlayerAction import PlayerAction


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

    def to_direction_tuple(self):
        if self == PlayerDirection.UP:
            return 0, -1
        if self == PlayerDirection.DOWN:
            return 0, 1
        if self == PlayerDirection.LEFT:
            return -1, 0
        if self == PlayerDirection.RIGHT:
            return 1, 0

    def invert(self):
        return PlayerDirection(((self.value + 2) % 4) + 1)


class PlayerState:
    def __init__(self, direction: PlayerDirection, speed: int, x_position: int, y_position: int, game_round: int = 1):
        self.direction = direction
        self.speed = speed
        self.position_x = x_position
        self.position_y = y_position
        self.game_round = game_round

        self.previous: [PlayerState] = []
        self.all_steps = {(x_position, y_position): self}
        self.action = None
        self.steps_to_this_point = []
        self.collided_with_own_line = False
        # This field is optional for algorithms that determine the risk for this step
        self.optional_risk = 0.0
        self.success_probability = 1.0

    def do_action(self, action: PlayerAction):
        if self.action is not None:
            raise Exception('An action has already been executed')

        self.action = action
        if self.action == PlayerAction.TURN_LEFT or self.action == PlayerAction.TURN_RIGHT:
            self.direction = self.direction.turn(self.action)
        elif self.action == PlayerAction.SLOW_DOWN:
            self.speed -= 1
        elif self.action == PlayerAction.SPEED_UP:
            self.speed += 1

    def do_move(self) -> object:
        if self.action is None:
            raise Exception('No action has been performed yet')

        child = self.copy()
        child.action = None

        x_offset = 0
        y_offset = 0

        if self.direction == PlayerDirection.UP:
            child.position_y -= self.speed
            y_offset = -1
        elif self.direction == PlayerDirection.RIGHT:
            child.position_x += self.speed
            x_offset = 1
        elif self.direction == PlayerDirection.DOWN:
            child.position_y += self.speed
            y_offset = 1
        elif self.direction == PlayerDirection.LEFT:
            child.position_x -= self.speed
            x_offset = -1

        # Calculate the new steps
        child.steps_to_this_point = list(Board.get_points_in_rectangle(self.position_x + x_offset,
                                                                       self.position_y + y_offset,
                                                                       child.position_x,
                                                                       child.position_y))
        # Remove the jumped over cells
        do_jump = self.game_round % 6 == 0
        while do_jump and len(child.steps_to_this_point) > 2:
            child.steps_to_this_point.pop(1)

        # Add self to previous of child
        child.previous.append(self)

        # All new passed positions
        for step in child.steps_to_this_point:
            child.collided_with_own_line |= bool(child.all_steps.get(step, False))
            if not child.collided_with_own_line:
                child.all_steps.setdefault(step, child)

        # Increase round number
        child.game_round += 1

        return child

    def verify_speed(self):
        # check for speed conditions
        return 0 < self.speed <= 10

    def verify_state(self, board: Board) -> bool:
        # check for speed conditions and if the new position is on the board
        return self.verify_speed() and board.point_is_on_board(self.position_x, self.position_y)

    def verify_move(self, board: Board) -> bool:
        if not self.verify_state(board):
            return False

        # check for collisions with other players
        # check for collisions with myself
        for step in self.steps_to_this_point:
            if not board.point_is_available(step[0], step[1]) or self.collided_with_own_line:
                return False

        return True

    def get_position_tuple(self) -> Tuple[int, int]:
        return self.position_x, self.position_y

    def copy(self):
        copy = PlayerState(self.direction, self.speed, self.position_x, self.position_y, self.game_round)
        copy.previous = self.previous.copy()
        copy.action = self.action
        copy.all_steps = self.all_steps.copy()
        copy.steps_to_this_point = self.steps_to_this_point.copy()
        copy.optional_risk = self.optional_risk
        copy.success_probability = self.success_probability
        return copy

    def __str__(self):
        return f'pos = ({self.position_x}, {self.position_y}), speed = {self.speed}, direction = {self.direction}, round = {self.game_round}'
