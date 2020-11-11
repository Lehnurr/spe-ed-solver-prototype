import time
from game_data.game.Board import Board
from game_data.player.PlayerState import PlayerState, PlayerAction
import numpy as np
from collections import deque


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


def calculate_reachable_points_weighted(
        initial_player_state: PlayerState,
        initial_step_offset: int,
        board: Board,
        risk_array: np.ndarray,
        min_step_array: np.ndarray,
        calculation_limit: int) -> np.ndarray:

    reachable_points = np.zeros((board.height, board.width))
    initial_weight = 1
    queue = deque()
    queue.append((initial_step_offset, initial_weight, initial_player_state))

    calculations = 0

    while calculations <= calculation_limit:

        if len(queue) == 0:
            break

        local_step_offset, local_weight, local_base_state = queue.popleft()

        calculations += 1

        if local_base_state.verify_move(board):
            highest_risk = 0
            for x, y in local_base_state.steps_to_this_point:
                highest_risk = max(highest_risk, risk_array[y, x])
                # invert risk when own player reaches point first
                # inverted risk as reward for cutting of other players
                if min_step_array[y, x] > local_step_offset:
                    highest_risk = -highest_risk
            weight = (1 - highest_risk) * local_weight
            reachable_points[local_base_state.position_y, local_base_state.position_x] += weight

            for action in PlayerAction:
                state_copy = local_base_state.copy()
                state_copy.do_action(action)
                state_variation = state_copy.do_move()
                queue.append((local_step_offset + 1, weight, state_variation))

    return reachable_points
