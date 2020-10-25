from random import random
from typing import Dict, Tuple
from analysis.full_range.next_range import calculate_next_states
from game_data.game.Board import Board
from game_data.player.PlayerState import PlayerDirection, PlayerState


ROUND_WEIGHT = 0.5


def calculate_ranges_for_player(game_board: Board, initial_state: PlayerState, lookup_round_count: int = -1) \
        -> Dict[Tuple[int, int], Dict[PlayerDirection, Dict[int, PlayerState]]]:
    result_data = {}
    next_states = [initial_state]

    current_round = 0
    while len(next_states) > 0 and lookup_round_count != next_states[0]:
        next_states = calculate_next_states(game_board, next_states, result_data)

        for state in next_states:
            # game_round weighted state_risk
            state_round_weight = state.game_round - initial_state.game_round * ROUND_WEIGHT
            state_risk = (state_round_weight + sum([game_board[s[1]][s[0]] for s in state.steps_to_this_point])) \
                         / (state_round_weight + len(state.steps_to_this_point))

            # continue with the higher risk
            state.optional_risk = max(state_risk, state.previous[-1].optional_risk)

        current_round += 1

    return result_data
