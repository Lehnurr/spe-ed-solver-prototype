from game_data.player.PlayerState import PlayerDirection
from game_data.player.PlayerAction import PlayerAction
from game_data.game.Board import Board
from typing import Tuple


class BackwardPlayerState:
    def __init__(self, direction: PlayerDirection, speed: int, x_position: int, y_position: int, round_modulo: int = -1):
        self.direction = direction
        self.speed = speed
        self.position_x = x_position
        self.position_y = y_position

        self.previous: [BackwardPlayerState] = []
        self.all_steps = {(x_position, y_position): self}
        self.action = None
        self.steps_to_this_point = []
        self.collided_with_own_line = False

        self.roundModulo = -1

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

    def do_move(self, board: Board) -> object:
        if self.action is None:
            raise Exception('No action has been performed yet')

        child = self.copy()
        child.action = None

        x_offset, y_offset = self.direction.to_direction_tuple()

        if self.direction == PlayerDirection.UP:
            child.position_y -= self.speed
        elif self.direction == PlayerDirection.RIGHT:
            child.position_x += self.speed
        elif self.direction == PlayerDirection.DOWN:
            child.position_y += self.speed
        elif self.direction == PlayerDirection.LEFT:
            child.position_x -= self.speed

        # Calculate the new steps
        child.steps_to_this_point = list(Board.get_points_in_rectangle(self.position_x + x_offset,
                                                                       self.position_y + y_offset,
                                                                       child.position_x,
                                                                       child.position_y))

        jump_needed = False
        for x, y in child.steps_to_this_point[1:-1]:
            if board.point_is_available(x, y):
                jump_needed = True

        if jump_needed and self.roundModulo == -1:
            self.roundModulo = 0

        # Remove the jumped over cells
        do_jump = self.roundModulo == 0
        while do_jump and len(child.steps_to_this_point) > 2:
            child.steps_to_this_point.pop(1)

        # Add self to previous of child
        child.previous.append(self)

        # All new passed positions
        for step in child.steps_to_this_point:
            child.collided_with_own_line |= bool(child.all_steps.get(step, False))
            if not child.collided_with_own_line:
                child.all_steps.setdefault(step, child)

        # Increase round modulo
        if self.roundModulo == -1:
            child.roundModulo = -1
        else:
            child.roundModulo = (self.roundModulo + 1) % 6

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
        copy = BackwardPlayerState(self.direction, self.speed, self.position_x, self.position_y, self.roundModulo)
        copy.previous = self.previous.copy()
        copy.action = self.action
        copy.all_steps = self.all_steps.copy()
        copy.steps_to_this_point = self.steps_to_this_point.copy()
        return copy

    def __str__(self):
        return f'pos = ({self.position_x}, {self.position_y}), speed = {self.speed}, direction = {self.direction}, modulo = {self.roundModulo}'