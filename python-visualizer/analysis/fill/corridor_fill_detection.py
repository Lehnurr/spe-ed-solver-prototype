import numpy as np
from analysis.fill.CorridorDetection import CorridorDetection
from game_data.player.PlayerState import PlayerState
from game_data.player.PlayerAction import PlayerAction
from game_data.game.Board import Board
from typing import Dict
from analysis.area_detection import safe_area_detection


__CORRIDOR_DETECTION = CorridorDetection()


def determine_fill_values(
        player_state: PlayerState,
        board: Board) -> Dict[PlayerAction, float]:

    input_array = np.array(board.cells)

    original_safe_area_count = safe_area_detection.count_safe_areas(input_array)

    fill_result = {}

    for action in PlayerAction:

        fill_result[action] = 1.

        local_base_state = player_state.copy()
        local_base_state.do_action(action)
        local_next_state = local_base_state.do_move()

        adapted_array = np.array(board.cells)

        for x, y in local_next_state.steps_to_this_point:
            adapted_array[y, x] = 1.

        adapted_labels = safe_area_detection.get_labels(adapted_array)
        adapted_safe_area_count = safe_area_detection.count_labels(adapted_labels)

        if adapted_safe_area_count > original_safe_area_count:
            fill_result[action] = 0.

        else:
            x_pos, y_pos = local_next_state.position_x, local_next_state.position_y
            corridor_sub_map = __CORRIDOR_DETECTION.get_corridor_sub_map(adapted_array, x_pos, y_pos)

            if np.count_nonzero(corridor_sub_map) > 0:
                fill_result[action] = 0.5

    return fill_result
