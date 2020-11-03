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


def determine_future_cutting_values(
        player_state: PlayerState,
        input_array: np.ndarray,
        board: Board,
        search_length: int,
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
        if count_safe_areas(working_array) > base_label_count:
            return 1 - ((step_idx + 1) / search_length)
        speed = max(1, speed - 1)

    return 0.


def determine_cutting_values(
        player_state: PlayerState,
        board: Board,
        search_length: int = 1) -> Dict[PlayerAction, float]:

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
                local_cutting_value = determine_future_cutting_values(player_state, adapted_array, board,
                                                                      search_length, original_label_count)

        else:
            local_cutting_value = 1.

        result_cutting_values[action] = local_cutting_value

    return result_cutting_values
