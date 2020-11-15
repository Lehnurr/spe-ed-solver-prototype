from enum import Enum
from typing import Tuple, Dict, List

from analysis.full_range.no_risk_full_range import calculate_ranges_for_player
from draw.lol import LOL_PATTERN
from game_data.game.Board import Board
from game_data.player.PlayerAction import PlayerAction
from game_data.player.PlayerState import PlayerState


class Drawable(Enum):
    LOL = 1
    RIP = 2


class DrawingPatternPoint:
    def __init__(self, x_change: int, y_change: int, is_obligatory: bool = True):
        self.x_change = x_change
        self.y_change = y_change
        self.is_obligatory = is_obligatory

    def copy(self):
        return DrawingPatternPoint(self.x_change, self.y_change, self.is_obligatory)

    def copy_invert(self):
        return DrawingPatternPoint(-self.x_change, -self.y_change, self.is_obligatory)


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


def __get_possible_next_steps(possible_states, pattern, start_index) -> List[PlayerState]:
    valid_states = []
    for state in possible_states:
        # verified if all steps_to_this_point are on the pattern
        is_valid = True
        current_index = start_index
        current_x = state.position_x
        current_y = state.position_y
        for step in state.steps_to_this_point:
            if step[0] != current_x or step[1] != current_y:
                if pattern[current_index].is_obligatory:
                    is_valid = False
                    break
                else:
                    # not-obligatory cells can be jumped over
                    current_index += 1
                    continue
            else:
                current_x += pattern[current_index].x_change
                current_y += pattern[current_index].y_change
                current_index += 1
        if is_valid:
            valid_states.append(state)

    return valid_states


def __get_possible_actions(pattern, board, player_state, start_index) -> Dict[PlayerAction: int]:
    current_x = player_state.position_x
    current_y = player_state.position_y

    # Check if all needed cells are available and draw border around the pattern
    for point in pattern[start_index:]:
        new_x = current_x + point.x_change
        new_y = current_y + point.y_change

        if board[new_y][new_x] == -2:
            # cell was set as border, but is needed
            board[new_y][new_x] = 0
        elif board[new_y][new_x] != 0:
            # cell is not empty
            if point.is_obligatory:
                return False
            continue

        # draw border around the needed cell with value = -2
        for neighbor in board.get_neighbors(current_x, current_y):
            if neighbor[0] != current_x or neighbor[1] != current_y:
                board[neighbor[1]][neighbor[0]] = -2

        current_x = new_x
        current_y = new_y

    # do full_range for the next possible steps with max precision
    possible_states = [state for directions in calculate_ranges_for_player(board, player_state, 1).values()
                       for speeds in directions.values()
                       for state in speeds.values()]

    # verify the possible states
    valid_states = __get_possible_next_steps(possible_states, pattern, start_index)

    for state in valid_states:
        is_valid = True
        # check if this action can reach the end or speed = 1
        st = state.copy()
        current_x = st.position_x
        current_y = st.position_y
        current_index = start_index

        while current_index < len(pattern):
            point = pattern[current_index]
            current_x += point.x_change
            current_y -= point.y_change
            if st.speed == 1:
                break

            possible_states = [st1 for directions in
                               calculate_ranges_for_player(board, st, 1).values()
                               for speeds in directions.values()
                               for st1 in speeds.values()]

            valid_actions = {state.previous[-1].action: len(state.steps_to_this_point)
                             for state in __get_possible_next_steps(possible_states, pattern, current_index)}

            # choose one step, preferred slow down, TL, TR, CN
            if PlayerAction.SLOW_DOWN in valid_actions:
                current_index += valid_actions[PlayerAction.SLOW_DOWN]
                continue
            elif PlayerAction.TURN_LEFT in valid_actions:
                current_index += valid_actions[PlayerAction.TURN_LEFT]
                continue
            elif PlayerAction.TURN_RIGHT in valid_actions:
                current_index += valid_actions[PlayerAction.TURN_RIGHT]
                continue
            elif PlayerAction.CHANGE_NOTHING in valid_actions:
                current_index += valid_actions[PlayerAction.CHANGE_NOTHING]
                continue
            else:
                is_valid = False
                break

        if is_valid:
            valid_states.append(state)

    return {state.previous[-1].action: start_index + len(state.steps_to_this_point) for state in valid_states}


def get_draw_action(drawing: Drawable, player_state: PlayerState, board: Board, start_index: int = 0) \
        -> List[Tuple[PlayerAction: int]]:
    # def return variable to return all possible actions
    possible_actions: List[Tuple[PlayerAction: int]] = []

    # check if drawing this pattern is possible
    if start_index >= 0:
        pattern = get_pattern(drawing)
        possible_actions += list(__get_possible_actions(pattern, board.copy(), player_state, abs(start_index)).items())

    # check if drawing the inverted pattern is possible
    if start_index <= 0:
        inverted_pattern = get_pattern(drawing, True)
        possible_actions += [(action, -new_start_index)
                             for action, new_start_index
                             in __get_possible_actions(inverted_pattern, board.copy(), player_state, abs(start_index))
                             .items()]

    # return possible actions with the next start_index
    return possible_actions
