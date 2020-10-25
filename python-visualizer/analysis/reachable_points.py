import time
from game_data.game.Board import Board
from game_data.player.PlayerState import PlayerState, PlayerAction
import numpy as np


def calculate_reachable_points(initial_player_state: PlayerState, board: Board, timeout: float = 0.0) -> np.ndarray:

    reachable_points = np.zeros((board.height, board.width))
    queue = [initial_player_state]

    start_time = time.time()

    while time.time() - start_time < timeout and timeout > 0.0:
        if len(queue) == 0:
            break
        local_base_state = queue.pop(0)
        for action in PlayerAction:
            state_copy = local_base_state.copy()
            state_copy.do_action(action)
            state_variation = state_copy.do_move()
            if state_variation.verify_move(board):
                queue.append(state_variation)
                reachable_points[state_variation.position_y, state_variation.position_x] = 1

    return reachable_points
