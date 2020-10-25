from random import random
from typing import Dict, Tuple
from analysis.full_range.next_range import calculate_next_states
from game_data.game.Board import Board
from game_data.player.PlayerState import PlayerDirection, PlayerState

# WARNING: this Kind of risk evaluation is bullshit,
# because a path with 10 rounds & an average of 0.50
# is better than a 2-Round Way with a average of 0.6


def calculate_ranges_for_player(game_board: Board, initial_state: PlayerState, lookup_round_count: int = -1) \
        -> Dict[Tuple[int, int], Dict[PlayerDirection, Dict[int, PlayerState]]]:

    result_data = {}
    next_states = [initial_state]

    current_round = 0
    while len(next_states) > 0 and lookup_round_count != current_round:
        next_states = calculate_next_states(game_board, next_states, result_data)

        # Weight next_status
        for state in next_states:
            step_risk_sum = 0
            step_count = 0
            for step in state.steps_to_this_point:
                step_risk_sum += game_board[step[1]][step[0]]
                step_count += 1

            state_risk = step_risk_sum / step_count

            prev_length = len(state.previous) - 1
            prev_risk = state.previous[-1].optional_risk
            state.optional_risk = (state_risk + prev_risk * prev_length) / (prev_length + 1)

        current_round += 1

    return result_data


if __name__ == "__main__":
    board = Board(5, 10)
    for i in range(0, board.height):
        for j in range(0, board.width):
            board[i][j] = random()

    calculate_ranges_for_player(board, PlayerState(PlayerDirection.RIGHT, 1, 0, 0))

