from game_data.player.PlayerState import PlayerState, PlayerDirection
from game_data.player.PlayerAction import PlayerAction
from game_data.game.Board import Board
import heapq
from analysis.bidirectional_path_finding.BackwardPlayerState import BackwardPlayerState
import multiprocessing as mp
import numpy as np
from typing import Dict, Tuple, Set
from collections import namedtuple
import math
import time


Intake = namedtuple("Intake", "x y direction speed round_modulo")

STEPS_FILL_VALUE = 100000
MAX_STATE_CALCULATIONS_PER_POINT = 100


def manhattan_distance_2d(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
    return abs(v1[0] - v2[0]) + abs(v1[1] - v2[1])


def recursive_forward_search(board: Board, local_base_state: PlayerState, action: PlayerAction, start_round: int,
                             enemy_probability: np.ndarray, enemy_min_steps: np.ndarray,
                             max_depth: int, current_depth: int = 0) \
        -> Dict[Intake, Tuple[int, float]]:
    local_state_copy = local_base_state.copy()
    local_state_copy.do_action(action)
    local_next_state = local_state_copy.do_move()

    result = {}

    if local_next_state.verify_move(board):

        if current_depth <= max_depth:
            for action in PlayerAction:
                result.update(recursive_forward_search(board, local_next_state, action, start_round,
                                                       enemy_probability, enemy_min_steps,
                                                       max_depth, current_depth + 1))

        max_probability = 0
        for x, y in local_next_state.steps_to_this_point:
            if enemy_min_steps[y, x] < current_depth:
                max_probability = max(max_probability, enemy_probability[y, x])
        rating = (1 - max_probability) * local_base_state.success_probability
        local_next_state.success_probability = rating

        intake = Intake(local_next_state.position_x, local_next_state.position_y, local_next_state.direction,
                        local_next_state.speed, local_next_state.game_round % 6)
        if not (intake in result.keys() and rating > result[intake][1]):
            result[intake] = (local_next_state.game_round - start_round, rating)

    return result


def calculate_target_center(target_dict: Dict[PlayerAction, Tuple[int, int]]) -> Tuple[float, float]:
    x_sum = 0.
    y_sum = 0.
    for x, y in target_dict.values():
        x_sum += x
        y_sum += y
    elem_count = max(len(target_dict), 1)
    return x_sum / elem_count, y_sum / elem_count


def backward_aggregate_paths(target_dict: Dict[PlayerAction, Tuple[int, int]], share: list, board: Board,
                             enemy_probability: np.ndarray, enemy_min_steps: np.ndarray,
                             action_intake_map: Dict[PlayerAction, Dict[Intake, Tuple[int, float]]], timeout: float) \
        -> Dict[PlayerAction, Tuple[np.ndarray, np.ndarray]]:

    result = {action: (np.ones((board.height, board.width)) * STEPS_FILL_VALUE, np.zeros((board.height, board.width)))
              for action in PlayerAction}

    global_target_center = calculate_target_center(target_dict)

    process_priority_queue = []
    for x, y in share:
        point = (x, y)
        heapq.heappush(process_priority_queue, (manhattan_distance_2d(point, global_target_center), point))

    start_time = time.time()
    while time.time() - start_time < timeout and len(process_priority_queue) > 0:
        priority, start_point = heapq.heappop(process_priority_queue)

        local_queue = [((speed - 1) * 100., BackwardPlayerState(direction, speed, start_point[0], start_point[1]))
                       for direction in PlayerDirection
                       for speed in range(1, 11)]
        heapq.heapify(local_queue)

        local_target_dict = target_dict.copy()
        local_target_center = global_target_center
        calculations = 0

        while len(local_target_dict) > 0 and len(local_queue) > 0 and calculations < MAX_STATE_CALCULATIONS_PER_POINT:
            calculations += 1
            priority, backward_state = heapq.heappop(local_queue)

            if backward_state.verify_move(board):

                # gather for possible intakes
                if backward_state.roundModulo == -1:
                    intake_checks = [Intake(backward_state.position_x, backward_state.position_y,
                                     backward_state.direction.invert(), backward_state.speed,
                                     round_modulo) for round_modulo in range(0, 6)]
                else:
                    intake_checks = [Intake(backward_state.position_x, backward_state.position_y,
                                     backward_state.direction.invert(), backward_state.speed,
                                     backward_state.roundModulo)]

                # check if intakes exist for actions
                for action in list(local_target_dict.keys()):
                    recalculate_target = False
                    for intake_check in intake_checks:
                        if intake_check in action_intake_map[action].keys():

                            # recalculate target
                            recalculate_target = True

                            # save new intakes
                            steps, rating = action_intake_map[action][intake_check]
                            for prev_state in reversed([backward_state] + backward_state.previous):

                                x_base, y_base = prev_state.position_x, prev_state.position_y
                                steps += 1

                                max_probability = 0
                                for x, y in prev_state.steps_to_this_point:
                                    if enemy_min_steps[y, x] < steps:
                                        max_probability = max(max_probability, enemy_probability[y, x])
                                rating *= 1 - max_probability

                                new_intake = Intake(x_base, y_base, prev_state.direction.invert(), prev_state.speed,
                                                    prev_state.roundModulo)

                                if new_intake not in action_intake_map[action].keys() or \
                                        action_intake_map[action][new_intake][1] > rating:
                                    action_intake_map[action][new_intake] = (steps, rating)
                                    result[action][0][y_base, x_base] = steps
                                    result[action][1][y_base, x_base] = rating

                    if recalculate_target:
                        local_target_dict.pop(action)
                        local_target_center = calculate_target_center(local_target_dict)

                # add children
                for action in PlayerAction:
                    state_copy = backward_state.copy()
                    state_copy.do_action(action)
                    next_state = state_copy.do_move(board)
                    next_priority = \
                        manhattan_distance_2d((next_state.position_x, next_state.position_y), local_target_center)
                    heapq.heappush(local_queue, (next_priority, next_state))

    return result


class BidirectionalPathFinder:

    def __init__(self, board: Board, search_depth: int, timeout: float):
        self.actionIntakeMaps = {}
        self.processingSet = set()
        self.board = board
        self.baseState = PlayerState(PlayerDirection.UP, -1, -1, -1, -1)
        self.pointsToProcess = []

        self.searchDepth = search_depth
        self.timeout = timeout

        self.result_steps_map = {}
        self.result_rating_map = {}

    def update(self, board: Board, player_state: PlayerState, enemy_probability: np.ndarray, enemy_min_steps: np.ndarray):
        self.baseState = player_state
        self.board = board
        self.processingSet = {(point[1], point[0]) for point in np.argwhere(np.array(self.board.cells) == 0).tolist()}
        self.__initialize_forward_actions(enemy_probability, enemy_min_steps, self.searchDepth)
        self.__aggregate_paths(self.timeout, enemy_probability, enemy_min_steps)

    def __initialize_forward_actions(self, enemy_probability: np.ndarray, enemy_min_steps: np.ndarray, depth: int):
        action_array = list(PlayerAction)
        argument_array = [(self.board, self.baseState, action, self.baseState.game_round, enemy_probability, enemy_min_steps, depth)
                          for action in action_array]
        pool = mp.Pool(mp.cpu_count())
        result_array = pool.starmap(recursive_forward_search, argument_array)
        pool.close()
        pool.join()
        result = {}
        for idx in range(len(action_array)):
            result[action_array[idx]] = result_array[idx]
        self.actionIntakeMaps = result

    def __aggregate_paths(self, timeout: float, enemy_probability: np.ndarray, enemy_min_steps: np.ndarray):

        total_points = list(self.processingSet)

        # sort by angle to base position
        total_points.sort(key=lambda p: math.atan2(p[1] - self.baseState.position_y, p[0] - self.baseState.position_x))

        # get shares of points to process
        shares = np.array_split(total_points, mp.cpu_count())

        # get targets
        target_dict = {}
        for action in PlayerAction:
            local_state = self.baseState.copy()
            local_state.do_action(action)
            local_next_state = local_state.do_move()
            if local_next_state.verify_move(self.board):
                target_dict[action] = (local_next_state.position_x, local_next_state.position_y)

        # launch processes
        pool = mp.Pool(mp.cpu_count())
        arguments = [(target_dict, share, self.board, enemy_probability, enemy_min_steps, self.actionIntakeMaps, timeout)
                     for share in shares]
        result_array = pool.starmap(backward_aggregate_paths, arguments)
        pool.close()
        pool.join()

        # save results
        steps_result = {action: np.ones((self.board.height, self.board.width)) * STEPS_FILL_VALUE
                        for action in PlayerAction}
        rating_result = {action: np.zeros((self.board.height, self.board.width))
                         for action in PlayerAction}
        for result in result_array:
            for action in PlayerAction:
                steps_result[action] = np.minimum(steps_result[action], result[action][0])
                rating_result[action] = np.maximum(rating_result[action], result[action][1])

        for action in PlayerAction:
            steps_result[action][steps_result[action] >= STEPS_FILL_VALUE] = 0
        self.result_steps_map = steps_result
        self.result_rating_map = rating_result

    def get_result_steps_map(self) -> Dict[PlayerAction, np.ndarray]:
        return self.result_steps_map

    def get_result_rating_map(self) -> Dict[PlayerAction, np.ndarray]:
        return self.result_rating_map
