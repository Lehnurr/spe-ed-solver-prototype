import numpy as np
from skimage import measure
from game_data.player.PlayerState import PlayerState
from game_data.player.PlayerAction import PlayerAction
from game_data.game.Board import Board
from typing import Dict


def count_safe_areas(input_array: np.ndarray) -> int:
    working_array = np.ones(input_array.shape)
    working_array[input_array != 0] = 0
    labels = measure.label(working_array, background=0, connectivity=1)
    label_count = np.max(labels)
    return label_count


def determine_cutting_values(player_state: PlayerState, board: Board, depth: int = 1) -> Dict[PlayerAction, float]:

    original_label_count = count_safe_areas(np.array(board.cells))

    result_cutting_values = {}

    for action in PlayerAction:
        local_base_state = player_state.copy()
        local_base_state.do_action(action)
        local_next_state = local_base_state.do_move()

        if local_next_state.verify_move(board):

            adapted_array = np.array(board.cells)

            for x, y in local_next_state.steps_to_this_point:
                adapted_array[y, x] = 1

            if count_safe_areas(adapted_array) > original_label_count:
                local_cutting_value = 1.
            else:
                if depth > 1:
                    recursion_result = determine_cutting_values(local_next_state, board, depth - 1)
                    recursion_cutting_value = min(recursion_result.values())
                    local_cutting_value = recursion_cutting_value / 2
                else:
                    local_cutting_value = 0.

        else:
            local_cutting_value = 1.

        result_cutting_values[action] = local_cutting_value

    return result_cutting_values
