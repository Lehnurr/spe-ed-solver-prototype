from enum import Enum
from typing import Tuple, Dict, List

from game_data.player.PlayerAction import PlayerAction


class Drawable(Enum):
    LOL = 1


class DrawingPatternPoint:
    def __init__(self, x_change: int, y_change: int, is_obligatory: bool = True):
        self.x_change = x_change
        self.y_change = y_change
        self.is_obligatory = is_obligatory

    def copy(self):
        return DrawingPatternPoint(self.x_change, self.y_change, self.is_obligatory)

    def copy_invert(self):
        return DrawingPatternPoint(-self.x_change, -self.y_change, self.is_obligatory)


def get_pattern(drawing) -> List[DrawingPatternPoint]:
    # TODO: load pattern as a copy from file / config
    pass


def can_draw(pattern, board, playerState, start_index, step):
    # TODO: check if drawing (pattern should already be inverted) is possible.
    pass


def get_inversion(pattern: List[DrawingPatternPoint]) -> List[DrawingPatternPoint]:
    return [point.copy_invert() for point in pattern]


def calculate_needed_turn(point_a: DrawingPatternPoint, point_b: DrawingPatternPoint):
    a = point_a.copy()
    b = point_b.copy()

    if point_b.y_change != 0:
        b = b.copy_invert()

    if abs(a.x_change + b.y_change) == 2 or abs(a.y_change + b.x_change) == 2:
        return PlayerAction.TURN_LEFT

    if a.x_change + b.y_change == 0 or a.y_change + b.x_change == 0:
        return PlayerAction.TURN_RIGHT

    return None


def get_draw_action(drawing: Drawable, playerState, board, start_index: int = 0) -> Dict[PlayerAction: int]:
    # get pattern for the selected drawable
    initial_pattern = get_pattern(drawing)

    # holds all drawable Patterns an the step direction (-1 for inverted patterns)
    patterns: Dict[int: List[DrawingPatternPoint]] = {}

    # check if drawing this pattern is possible
    if start_index >= 0 and can_draw(initial_pattern, board, playerState, start_index, 1):
        patterns[1] = initial_pattern

    # check if drawing the inverted pattern is possible
    if start_index <= 0:
        inverted_pattern = get_inversion(initial_pattern)
        if can_draw(inverted_pattern, board, playerState, start_index, -1):
            patterns[-1] = inverted_pattern

    # def return variable to return all possible actions
    possible_actions: Dict[PlayerAction: int] = {}

    # determine all possible actions (2 patterns are only possible if start_index == 0)
    for step, pattern in patterns.items():
        next_index = start_index + step

        # check if TURN_LEFT is needed
        if calculate_needed_turn(pattern[start_index], pattern[next_index]) == PlayerAction.TURN_LEFT:
            possible_actions[PlayerAction.TURN_LEFT] = next_index
            break
        # check if TURN_RIGHT is needed
        elif calculate_needed_turn(pattern[start_index], pattern[next_index]) == PlayerAction.TURN_RIGHT:
            possible_actions[PlayerAction.TURN_RIGHT] = next_index
            break
        # check all other possible actions
        else:
            pass
            # TODO: check if speed up is possible
            # TODO: check if speed down is possible
            # TODO: check if change nothig is possible

    # return possible actions with the next start_index
    return possible_actions
