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
    bins = list(np.bincount(updated_labels_masked))
    bins[0] = 0
    bins = [single_bin for single_bin in bins if single_bin > 0]
    cutting_proportion = min(bins) / sum(bins)
    return cutting_proportion


def determine_future_cutting_values(
        player_state: PlayerState,
        input_array: np.ndarray,
        board: Board,
        search_length: int,
        base_labels: np.ndarray,
        base_label_count: int):

    x_pos, y_pos = player_state.position_x, player_state.position_y
    speed = player_state.speed
    x_speed_factor, y_speed_factor = player_state.direction.to_direction_tuple()

    working_array = np.copy(input_array)

    for step_idx in range(search_length):
        for cell_step in range(speed):
            x_pos += x_speed_factor
            y_pos += y_speed_factor
            if board.point_is_available(x_pos, y_pos):
                working_array[y_pos, x_pos] = 1
            else:
                return 0.

        updated_labels = get_safe_areas_labels(working_array)
        updated_labels_count = get_safe_areas_label_count(updated_labels)
        if updated_labels_count > base_label_count:
            cutting_proportion = get_cutting_proportion(base_labels, (x_pos, y_pos), updated_labels)
            width_factor = 1 - ((step_idx + 1) / search_length)
            return width_factor * cutting_proportion
        speed = max(1, speed - 1)

    return 0.


def determine_cutting_values(
        player_state: PlayerState,
        board: Board,
        search_length: int = 1) -> Dict[PlayerAction, float]:

    original_array = np.array(board.cells)
    original_labels = get_safe_areas_labels(original_array)
    original_label_count = get_safe_areas_label_count(original_labels)

    result_cutting_values = {}

    for action in PlayerAction:
        local_base_state = player_state.copy()
        local_base_state.do_action(action)
        local_next_state = local_base_state.do_move()

        if local_next_state.verify_move(board):

            adapted_array = np.array(board.cells)

            for x, y in local_next_state.steps_to_this_point:
                adapted_array[y, x] = 1

            adapted_labels = get_safe_areas_labels(adapted_array)
            adapted_labels_count = get_safe_areas_label_count(adapted_labels)
            if adapted_labels_count > original_label_count:
                local_cutting_value = \
                    1. * get_cutting_proportion(original_labels,
                                                (local_next_state.position_x, local_next_state.position_y),
                                                adapted_labels)

            else:
                local_cutting_value = determine_future_cutting_values(player_state, adapted_array, board,
                                                                      search_length, original_labels,
                                                                      original_label_count)

        else:
            local_cutting_value = 1.

        result_cutting_values[action] = local_cutting_value

    return result_cutting_values
