import numpy as np
from skimage import measure
from game_data.player.PlayerState import PlayerState
from game_data.player.PlayerAction import PlayerAction
from game_data.game.Board import Board
from typing import Dict
from typing import Tuple


def get_safe_areas_labels(input_array: np.ndarray) -> np.ndarray:
    working_array = np.ones(input_array.shape)
    working_array[input_array != 0] = 0
    labels = measure.label(working_array, background=0, connectivity=1)
    return labels


def get_safe_areas_label_count(input_array: np.ndarray) -> int:
    return np.max(input_array)


def get_cutting_proportion(original_labels: np.ndarray, location: Tuple[int, int], updated_labels: np.ndarray):
    current_label = original_labels[location[1], location[0]]
    updated_labels_masked = np.copy(updated_labels)
    updated_labels_masked[original_labels != current_label] = 0
    bins = list(np.bincount(updated_labels_masked.flatten()))
    bins[0] = 0
    bins = [single_bin for single_bin in bins if single_bin > 0]
    cutting_proportion = min(bins) / sum(bins)
    return cutting_proportion


def determine_cutting_and_fill_values(
        player_state: PlayerState,
        board: Board,
        search_length: int) -> Tuple[Dict[PlayerAction, float], Dict[PlayerAction, float]]:

    original_array = np.array(board.cells)
    original_labels = get_safe_areas_labels(original_array)
    original_label_count = get_safe_areas_label_count(original_labels)

    result_fill_values = {}
    result_cutting_values = {}

    for action in PlayerAction:
        local_base_state = player_state.copy()
        local_base_state.do_action(action)
        local_next_state = local_base_state.do_move()

        fill_value = 0.
        cutting_value = 1.

        if local_next_state.verify_move(board):

            adapted_array = np.array(board.cells)

            for x, y in local_next_state.steps_to_this_point:
                adapted_array[y, x] = 1.

            adapted_labels = get_safe_areas_labels(adapted_array)
            adapted_labels_count = get_safe_areas_label_count(adapted_labels)

            if adapted_labels_count > original_label_count:
                cutting_value = 0.

            else:
                x, y = local_base_state.position_x, local_base_state.position_y
                x_direction, y_direction = local_next_state.direction.to_direction_tuple()

                for distance_idx in range(search_length):
                    x += x_direction
                    y += y_direction
                    if not board.point_is_available(x, y):
                        fill_value = 1 - ((distance_idx - 1) / search_length)
                        break

        result_fill_values[action] = fill_value
        result_cutting_values[action] = cutting_value

    return result_cutting_values, result_fill_values
