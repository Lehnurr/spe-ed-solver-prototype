from game_data.player.PlayerAction import PlayerAction
from game_data.player.PlayerState import PlayerState
from game_data.game.Board import Board
import numpy as np
from queue import Queue
import math


def calculate_probabilities_for_players(
        board: Board,
        player_states: [PlayerState],
        max_depth: int,
        invalid_move_weight: float = 1) -> np.ndarray:

    probabilities = np.zeros((board.height, board.height))

    for player_state in player_states:
        probabilities += calculate_probabilities_for_player(board, player_state, max_depth, invalid_move_weight)

    existing_cell_occupation = np.array(board.cells)
    probabilities[existing_cell_occupation != 0] = 1

    return probabilities


def calculate_probabilities_for_player(
        board: Board,
        initial_player_state: PlayerState,
        max_depth: int,
        invalid_move_weight: float = 1) -> np.ndarray:

    class QueueElement:
        def __init__(self, local_depth: int, local_player_state: PlayerState):
            self.depth = local_depth
            self.playerState = local_player_state

    probabilities = np.zeros((board.height, board.height))

    working_queue = Queue()
    working_queue.put(QueueElement(0, initial_player_state))

    while not working_queue.empty():

        queue_element = working_queue.get()
        depth = queue_element.depth
        player_state = queue_element.playerState

        for action in PlayerAction:

            new_player_state = player_state.copy()
            new_player_state.do_action(action)
            next_player_state = new_player_state.do_move()

            step_probability_factor = math.pow(1 / len(PlayerAction), depth)

            if not new_player_state.verify_move(board):
                step_probability_factor *= invalid_move_weight
            else:
                if depth < max_depth:
                    working_queue.put(QueueElement(depth + 1, next_player_state))

            affected_cells = next_player_state.steps_to_this_point

            for cell_x, cell_y in affected_cells:
                if board.point_is_on_board(cell_x, cell_y):
                    probabilities[cell_y, cell_x] += step_probability_factor

    return probabilities



