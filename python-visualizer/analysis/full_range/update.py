from typing import Dict, Tuple, List

from game_data.player.PlayerState import PlayerDirection, PlayerState


def update_full_range_result(current_game_round: int,
                             current_position: Tuple[int, int],
                             full_range_result: Dict[Tuple[int, int], Dict[PlayerDirection, Dict[int, PlayerState]]],
                             new_occupied_cells: List[Tuple[int, int]]) \
        -> Dict[Tuple[int, int], Dict[PlayerDirection, Dict[int, PlayerState]]]:
    new_result = {}
    for position, directions in full_range_result.items():
        for direction, speeds in directions.items():
            for speed, state in speeds.items():
                state_step_list = state.previous + [state]

                # discard, if the state is in the past
                if len(state_step_list) < current_game_round:
                    continue

                # discard, if this path originates not from the chosen action
                if state_step_list[current_game_round - 1].get_position_tuple() != current_position:
                    continue

                # discard if one of the new_occupied_cells is needed for this path
                if any(True for cell in new_occupied_cells if cell in state.all_steps):
                    continue

                # this path is still available -> add it to the new_result
                new_result\
                    .setdefault(position, {})\
                    .setdefault(direction, {})\
                    .setdefault(speed, state)

    return new_result
