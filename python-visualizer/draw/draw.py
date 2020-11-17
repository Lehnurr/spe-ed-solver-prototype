from enum import Enum
from typing import Tuple, Dict, List

from analysis.full_range.no_risk_full_range import calculate_ranges_for_player
from draw.DrawingPatternPoint import DrawingPatternPoint
from draw.lol import LOL_PATTERN
from draw.rip import RIP_PATTERN
from game_data.game.Board import Board
from game_data.player.PlayerAction import PlayerAction
from game_data.player.PlayerState import PlayerState


class Drawable(Enum):
    LOL = 1
    RIP = 2


def get_pattern(drawing: Drawable, invert=False) -> List[DrawingPatternPoint]:
    pattern = []
    if drawing == Drawable.LOL:
        pattern = LOL_PATTERN.copy()
    elif drawing == Drawable.RIP:
        pattern = RIP_PATTERN.copy()

    if invert:
        pattern = [point.copy_invert() for point in pattern]
        pattern.reverse()

    return pattern


def __get_possible_actions(pattern, board, player_state, start_index) -> Dict[PlayerAction, int]:
    # do full_range for the next possible steps with max precision
    possible_states = [state for directions in calculate_ranges_for_player(board, player_state, 1).values()
                       for speeds in directions.values()
                       for state in speeds.values()]

    # Get the valid states from the possible sates (States that are on the Path and can reach the end)
    valid_states = states_are_valid(board, pattern, start_index, possible_states)

    return {tup[0].previous[-1].action: tup[1] for tup in valid_states}


def states_are_valid(board, pattern, current_index, possible_states) -> List[Tuple[PlayerState, int]]:
    # break the recursion, because the path ends
    if current_index >= len(pattern):
        return [(state, current_index) for state in possible_states]

    valid_states = []

    for state in possible_states:
        # check if the steps of this state follows the path
        steps = [(state.previous[-1].position_x, state.previous[-1].position_y)] + state.steps_to_this_point

        new_step_index = current_index + steps_are_valid(steps, 1, pattern, current_index)

        if new_step_index <= current_index:
            continue

        # do full range and call xyz for the new results
        child_states = [state for directions in calculate_ranges_for_player(board, state, 1).values()
                        for speeds in directions.values()
                        for state in speeds.values()]

        # if min one child can travel the full path, this can also do
        if states_are_valid(board, pattern, new_step_index, child_states):
            valid_states.append((state, new_step_index % len(pattern)))

    return valid_states


def steps_are_valid(steps, step_index, pattern, pattern_index):
    if step_index < 1 or not (step_index < len(steps)) or not (pattern_index < len(pattern)):
        return 0

    prev_x, prev_y = steps[step_index - 1]
    current_x, current_y = steps[step_index]
    pattern_point = pattern[pattern_index]

    if prev_x + pattern_point.x_change == current_x and prev_y + pattern_point.y_change == current_y:
        moved_steps = steps_are_valid(steps, step_index + 1, pattern, pattern_index + 1)
        if moved_steps > -1:
            return 1 + moved_steps

    if pattern_point.is_obligatory:
        return -1
    else:
        moved_steps = steps_are_valid(steps, step_index, pattern, pattern_index + 1)
        return moved_steps + (0 if moved_steps == -1 else 1)


def get_draw_action(drawing: Drawable, player_state: PlayerState, board: Board, start_index: int = 0) \
        -> List[Tuple[PlayerAction, int]]:
    # def return variable to return all possible actions
    possible_actions: List[Tuple[PlayerAction, int]] = []

    # check if drawing this pattern is possible
    if start_index >= 0:
        pattern = get_pattern(drawing)
        if start_index < len(pattern):
            possible_actions += list(
                __get_possible_actions(pattern, board.copy(), player_state, abs(start_index)).items())

    # check if drawing the inverted pattern is possible
    if start_index <= 0:
        inverted_pattern = get_pattern(drawing, True)
        if abs(start_index) < len(inverted_pattern):
            possible_actions += [(action, -new_start_index)
                                 for action, new_start_index in
                                 __get_possible_actions(inverted_pattern, board.copy(), player_state, abs(start_index))
                                 .items()]

    # return possible actions with the next start_index
    return possible_actions
