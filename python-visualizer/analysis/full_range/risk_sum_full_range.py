from typing import Dict, Tuple
from analysis.full_range.next_range import calculate_next_states
from game_data.game.Board import Board
from game_data.player.PlayerState import PlayerDirection, PlayerState


def calculate_ranges_for_player(game_board: Board, initial_state: PlayerState, lookup_round_count: int = -1) \
        -> Dict[Tuple[int, int], Dict[PlayerDirection, Dict[int, PlayerState]]]:
    result_data = {}
    next_states = [initial_state]

    current_round = 0
    while len(next_states) > 0 and lookup_round_count != current_round:
        next_states = calculate_next_states(game_board, next_states, result_data)

        # TODO: Consider using the average or sum of the steps instead of the maximum step
        for state in next_states:
            # maximum for this steps
            state_max_risk = max([game_board[step[1]][step[0]] for step in state.steps_to_this_point])

            # add new maximum to the previous maxima
            state.optional_risk = state.previous[-1].optional_risk + state_max_risk

        current_round += 1

    return result_data
