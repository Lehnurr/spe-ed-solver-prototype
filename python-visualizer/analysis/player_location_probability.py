from game_data.player.PlayerAction import PlayerAction
from game_data.player.PlayerState import PlayerState
from game_data.game.Board import Board
import numpy as np
import time


def calculate_probabilities_for_players(
        board: Board,
        player_states: [PlayerState],
        depth: int) -> np.ndarray:

    probabilities = np.zeros((board.height, board.width))

    for player_state in player_states:
        probabilities = np.maximum(probabilities, calculate_probabilities_for_player(board, player_state, depth))

    existing_cell_occupation = np.array(board.cells)
    probabilities[existing_cell_occupation != 0] = 1

    return probabilities


def calculate_probabilities_for_player(
        board: Board,
        player_state: PlayerState,
        depth: int) -> np.ndarray:

    probabilities = np.zeros((board.height, board.width))

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

            if depth > 1:
                recursion_result = \
                    calculate_probabilities_for_player(board, next_player_state, depth - 1)
                probabilities += recursion_result * local_probability_factor

    return probabilities


