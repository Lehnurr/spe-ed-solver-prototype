from enum import Enum
from operator import attrgetter
from typing import List, Dict, Tuple

from game_data.player.PlayerAction import PlayerAction
from game_data.player.PlayerState import PlayerState, PlayerDirection


class FullRangePrecision(Enum):
    FULL_PRECISION = 1
    TWO_DIRECTIONS_FOUR_SPEEDS = 2
    ONE_DIRECTION_ONE_SPEED = 3

    @staticmethod
    def __get_speed_groups():
        return {
            1: [2],
            2: [1],
            3: [4],
            4: [3],
            5: [6, 7],
            6: [5, 7],
            7: [5, 6],
            8: [9, 10],
            9: [8, 10],
            10: [8, 9]
        }

    @staticmethod
    def get_precision_by_state_count(number_of_states: int):
        if number_of_states < 1200:
            return FullRangePrecision.FULL_PRECISION
        elif number_of_states < 2000:
            return FullRangePrecision.TWO_DIRECTIONS_FOUR_SPEEDS
        else:
            return FullRangePrecision.ONE_DIRECTION_ONE_SPEED

    @staticmethod
    def speed_is_already_set(current_speed: int, already_set_speeds: List[int], precision):
        ungrouped_speeds = list(already_set_speeds)

        if precision == FullRangePrecision.ONE_DIRECTION_ONE_SPEED and len(ungrouped_speeds) > 0:
            return True
        elif precision == FullRangePrecision.TWO_DIRECTIONS_FOUR_SPEEDS:
            for speed in already_set_speeds:
                ungrouped_speeds += precision.__get_speed_groups().get(speed, [])

        return current_speed in ungrouped_speeds


def replace_if_better(state, result_dict) -> bool:
    if state.optional_risk == 0:
        return False  # can't determine the better if there is no risk

    current_value = result_dict.get(state.direction, {}).get(state.speed, None)

    # True if it is replaced or added because its better than all equivalents.
    if current_value is None:
        current_min_risk = min([state for speed in result_dict.values() for state in speed.values()],
                               key=attrgetter('optional_risk')).optional_risk
        if state.optional_risk < current_min_risk:
            result_dict.setdefault(state.direction, {})[state.speed] = state
            return True
    elif current_value.optional_risk > state.optional_risk:
        result_dict[state.direction][state.speed] = state
        return True

    return False


def add_state_to_dict(state: PlayerState, result_dict, precision: FullRangePrecision) -> bool:
    direction = state.direction

    if precision == FullRangePrecision.ONE_DIRECTION_ONE_SPEED and len(result_dict) > 0:
        return replace_if_better(state, result_dict)
    elif precision == FullRangePrecision.FULL_PRECISION\
            and result_dict.get(state.direction, {}).get(state.speed, False):
        return replace_if_better(state, result_dict)
    elif precision == FullRangePrecision.TWO_DIRECTIONS_FOUR_SPEEDS:
        direction_left = direction.turn(PlayerAction.TURN_LEFT)
        direction_right = direction.turn(PlayerAction.TURN_RIGHT)
        if direction in result_dict.keys()\
                and FullRangePrecision.speed_is_already_set(state.speed, result_dict[direction].keys(), precision):
            return replace_if_better(state, result_dict)
        elif direction_left in result_dict.keys():
            if FullRangePrecision.speed_is_already_set(state.speed, result_dict[direction_left].keys(), precision):
                return replace_if_better(state, result_dict)
            direction = direction_left
        elif direction_right in result_dict.keys():
            if FullRangePrecision.speed_is_already_set(state.speed, result_dict[direction_right].keys(), precision):
                return replace_if_better(state, result_dict)
            direction = direction_right

    # Add state to the Dict
    sub_dict = result_dict.get(direction, {})
    sub_dict.setdefault(state.speed, state)
    result_dict[direction] = sub_dict
    return True
