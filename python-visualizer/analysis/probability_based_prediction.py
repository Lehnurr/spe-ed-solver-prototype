from game_data.player.PlayerAction import PlayerAction
from game_data.player.PlayerState import PlayerState
from game_data.game.Board import Board
import numpy as np
from typing import Tuple


# Unreachable value used for processing player step counts.
__INIT_VALUE_PLAYER_STEPS = 1000


def calculate_probabilities_for_players(
        board: Board,
        player_states: [PlayerState],
        depth: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Returns tuple of numpy arrays:
        - probability of reaching the given cells in the [depth] next steps
        - minimum amount of steps needed for a player to reach the cell
    """

    probabilities = np.zeros((board.height, board.width))
    min_player_steps = np.ones((board.height, board.width)) * __INIT_VALUE_PLAYER_STEPS

    for player_state in player_states:
        local_probabilities, local_min_player_steps = calculate_probabilities_for_player(board, player_state, depth)
        probabilities = np.maximum(probabilities, local_probabilities)
        min_player_steps = np.minimum(min_player_steps, local_min_player_steps)

    existing_cell_occupation = np.array(board.cells)
    probabilities[existing_cell_occupation != 0] = 1
    min_player_steps[min_player_steps == __INIT_VALUE_PLAYER_STEPS] = -1
    min_player_steps[existing_cell_occupation != 0] = 0

    return probabilities, min_player_steps


def calculate_probabilities_for_player(
        board: Board,
        player_state: PlayerState,
        depth: int,
        step_offset: int = 1) -> Tuple[np.ndarray, np.ndarray]:
    """
    Returns tuple of numpy arrays:
        - probability of reaching the given cells in the [depth] next steps
        - minimum amount of steps needed for the given player to reach the cell
    """

    probabilities = np.zeros((board.height, board.width))
    min_player_steps = np.ones((board.height, board.width)) * __INIT_VALUE_PLAYER_STEPS

    valid_player_state_tuples = []

    for action in PlayerAction:

        new_player_state = player_state.copy()
        new_player_state.do_action(action)
        next_player_state = new_player_state.do_move()

        if next_player_state.verify_move(board):
            valid_player_state_tuples.append((new_player_state, next_player_state))

    possible_action_count = len(valid_player_state_tuples)
    if possible_action_count > 0:
        local_probability_factor = 1 / possible_action_count

        for new_player_state, next_player_state in valid_player_state_tuples:

            affected_cells = next_player_state.steps_to_this_point
            for cell_x, cell_y in affected_cells:
                if board.point_is_on_board(cell_x, cell_y):
                    probabilities[cell_y, cell_x] += local_probability_factor
                    min_player_steps[cell_y, cell_x] = step_offset

            if depth > 1:
                recursion_probabilities, recursion_min_player_steps = \
                    calculate_probabilities_for_player(board, next_player_state, depth - 1, step_offset + 1)
                probabilities += recursion_probabilities * local_probability_factor
                min_player_steps = np.minimum(min_player_steps, recursion_min_player_steps)

    return probabilities, min_player_steps


