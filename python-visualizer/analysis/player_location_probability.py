
from game_data.player.PlayerAction import PlayerAction
from game_data.player.PlayerState import PlayerState
from game_data.game.Board import Board
import numpy as np


def calculate_probabilities_for_players(
        board: Board,
        player_states: [PlayerState],
        depth: int,
        invalid_move_weight: float = 1) -> np.ndarray:

    probabilities = np.zeros((board.height, board.height))

    for player_state in player_states:
        probabilities += calculate_probabilities_for_player(board, player_state, depth, invalid_move_weight)

    existing_cell_occupation = np.array(board.cells)
    probabilities[existing_cell_occupation != 0] = 1

    return probabilities


def calculate_probabilities_for_player(
        board: Board,
        player_state: PlayerState,
        depth: int,
        invalid_move_weight: float = 1) -> np.ndarray:

    probabilities = np.zeros((board.height, board.height))

    for action in PlayerAction:

        new_player_state = player_state.copy()
        new_player_state.do_action(action)
        next_player_state = new_player_state.do_move()

        validity_factor = 1 / len(PlayerAction)
        if not new_player_state.verify_move(board):
            validity_factor *= invalid_move_weight
        else:
            if depth > 1:
                recursion_result = \
                    calculate_probabilities_for_player(board, next_player_state, depth - 1, invalid_move_weight)
                probabilities += recursion_result * validity_factor

        affected_cells = next_player_state.steps_to_this_point

        for cell_x, cell_y in affected_cells:
            if board.point_is_on_board(cell_x, cell_y):
                probabilities[cell_y, cell_x] += validity_factor

    return probabilities


