from typing import List, Dict, Tuple
from analysis.full_range.FullRangePrecision import add_state_to_dict, FullRangePrecision
from game_data.game.Board import Board
from game_data.player.PlayerAction import PlayerAction
from game_data.player.PlayerState import PlayerDirection, PlayerState


def calculate_next_states(board: Board,
                          last_states: List[PlayerState],
                          previous_results: Dict[Tuple[int, int], Dict[PlayerDirection, Dict[int, PlayerState]]]
                          ) -> List[PlayerState]:

    if not (len(last_states) > 0):
        return []

    possible_next_states = list(do_actions(last_states))
    precision = FullRangePrecision.get_precision_by_state_count(len(possible_next_states))
    actual_next_states = []

    for state in possible_next_states:
        if not state.verify_move(board):
            continue  # remove state, (collision)

        position_dict = previous_results.get((state.position_x, state.position_y), {})
        if not add_state_to_dict(state, position_dict, precision):
            continue  # remove state, (there's already a similar solution)

        previous_results[(state.position_x, state.position_y)] = position_dict
        actual_next_states.append(state)

    return actual_next_states


def do_actions(state_list):
    for state in state_list:
        for action in PlayerAction:
            copy = state.copy()
            copy.do_action(action)
            yield copy.do_move()
