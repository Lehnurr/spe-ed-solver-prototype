import time
from datetime import datetime
from typing import Dict, Tuple
from analysis.full_range.next_range import calculate_next_states
from game_data.game.Board import Board
from game_data.player.PlayerState import PlayerDirection, PlayerState


def calculate_ranges_for_player(board: Board, initial_state: PlayerState, lookup_round_count: int = -1) \
        -> Dict[Tuple[int, int], Dict[PlayerDirection, Dict[int, PlayerState]]]:

    result_data = {}
    next_states = [initial_state]

    current_round = 0
    while len(next_states) > 0 and lookup_round_count != current_round:
        next_states = calculate_next_states(board, next_states, result_data)
        current_round += 1

    return result_data


if __name__ == "__main__":
    start = time.time()
    print(F"start full_range @{datetime.now().time()}")
    print(len(calculate_ranges_for_player(Board(64, 64), PlayerState(PlayerDirection.DOWN, 1, 4, 4)).keys()))
    end = time.time()
    print(F"total seconds: {end - start}")
    print(F"end full_range   @{datetime.now().time()}")

