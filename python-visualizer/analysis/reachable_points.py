import time
from game_data.game.Board import Board
from game_data.player.PlayerState import PlayerState, PlayerAction
import numpy as np


def calculate_reachable_points(initial_player_state: PlayerState, board: Board, timeout: int = 0) -> np.ndarray:

    reachable_points = np.zeros((board.height, board.width))
    queue = [initial_player_state]

    start_time = time.time()

    while time.time() - start_time < timeout or timeout == 0:
        if len(queue) == 0:
            break
        local_base_state = queue.pop(0)
        for action in PlayerAction:
            state_copy = local_base_state.copy()
            state_copy.do_action(action)
            state_variation = state_copy.do_move()
            if state_variation.verify_move(board):
                queue.append(state_variation)
                for x, y in state_variation.steps_to_this_point:
                    reachable_points[y, x] = 1

    return reachable_points
