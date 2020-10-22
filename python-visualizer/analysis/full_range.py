from datetime import datetime
from enum import Enum
from typing import List
import time

from game_data.game.Board import Board
from game_data.player.PlayerAction import PlayerAction
from game_data.player.PlayerState import PlayerDirection, PlayerState


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


def calculate_ranges_for_player(board: Board, initial_state: PlayerState, lookup_round_count: int = -1):
    result_data = {}
    next_states = [initial_state]
    current_round = 0
    while len(next_states) > 0 and lookup_round_count != current_round:
        possible_next_states = list(do_actions(next_states))
        next_states = []
        for state in possible_next_states:
            if not state.verify_move(board):
                continue  # remove state, (collision)

            position_dict = result_data.get((state.position_x, state.position_y), {})
            if not add_state_to_dict(state, position_dict, FullRangePrecision.get_precision_by_state_count(len(possible_next_states))):
                continue  # remove state, (there's already a similar solution)

            result_data[(state.position_x, state.position_y)] = position_dict
            next_states.append(state)
        current_round += 1

    return result_data


def do_actions(state_list):
    for state in state_list:
        for action in PlayerAction:
            copy = state.copy()
            copy.do_action(action)
            yield copy.do_move()


def add_state_to_dict(state: PlayerState, result_dict, precision: FullRangePrecision) -> bool:
    direction = state.direction

    if precision == FullRangePrecision.ONE_DIRECTION_ONE_SPEED and len(result_dict) > 0:
        return False
    elif precision == FullRangePrecision.FULL_PRECISION\
            and result_dict.get(state.direction, {}).get(state.speed, False):
        return False
    elif precision == FullRangePrecision.TWO_DIRECTIONS_FOUR_SPEEDS:
        direction_left = direction.turn(PlayerAction.TURN_LEFT)
        direction_right = direction.turn(PlayerAction.TURN_RIGHT)
        if direction in result_dict.keys()\
                and FullRangePrecision.speed_is_already_set(state.speed, result_dict[direction].keys(), precision):
            return False
        elif direction_left in result_dict.keys():
            if FullRangePrecision.speed_is_already_set(state.speed, result_dict[direction_left].keys(), precision):
                return False
            direction = direction_left
        elif direction_right in result_dict.keys():
            if FullRangePrecision.speed_is_already_set(state.speed, result_dict[direction_right].keys(), precision):
                return False
            direction = direction_right

    # Add state to the Dict
    sub_dict = result_dict.get(direction, {})
    sub_dict.setdefault(state.speed, state)
    result_dict[direction] = sub_dict
    return True


if __name__ == "__main__":
    start = time.time()
    print(F"start full_range @{datetime.now().time()}")
    print(len(calculate_ranges_for_player(Board(64, 64), PlayerState(PlayerDirection.DOWN, 1, 4, 4)).keys()))
    end = time.time()
    print(F"total seconds: {end - start}")
    print(F"end full_range   @{datetime.now().time()}")

