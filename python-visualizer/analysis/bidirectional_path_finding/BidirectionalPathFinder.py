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

MAX_STATE_CALCULATIONS_PER_POINT = 100


def manhattan_distance_2d(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
    return abs(v1[0] - v2[0]) + abs(v1[1] - v2[1])


def recursive_forward_search(board: Board, local_base_state: PlayerState,
                             action: PlayerAction, max_depth: int, current_depth: int = 0) \
        -> Dict[Intake, PlayerState]:
    local_state_copy = local_base_state.copy()
    local_state_copy.do_action(action)
    local_next_state = local_state_copy.do_move()

    result = {}

    if local_next_state.verify_move(board):

        if current_depth <= max_depth:
            for action in PlayerAction:
                result.update(recursive_forward_search(board, local_next_state, action, max_depth,
                                                       current_depth + 1))

        intake = Intake(local_next_state.position_x, local_next_state.position_y, local_next_state.direction,
                        local_next_state.speed, local_next_state.game_round % 6)
        result[intake] = local_next_state

    return result


def calculate_target_center(target_dict: Dict[PlayerAction, Tuple[int, int]]) -> Tuple[float, float]:
    x_sum = 0.
    y_sum = 0.
    for x, y in target_dict.values():
        x_sum += x
        y_sum += y
    elem_count = len(target_dict)
    return x_sum / elem_count, y_sum / elem_count


def backward_aggregate_paths(target_dict: Dict[PlayerAction, Tuple[int, int]], share: list, board: Board,
                             action_intake_map: Dict[PlayerAction, Dict[Intake, PlayerState]], timeout: float) \
        -> Dict[Intake, PlayerState]:

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
                # check for possible intakes
                for action in local_target_dict.keys():
                    if backward_state.roundModulo != -1:
                        intake = Intake(backward_state.position_x, backward_state.position_y,
                                        backward_state.direction.invert(), backward_state.speed,
                                        backward_state.roundModulo)
                        if intake in action_intake_map[action].keys():
                            print("exists")

                # add children
                for action in PlayerAction:
                    state_copy = backward_state.copy()
                    state_copy.do_action(action)
                    next_state = state_copy.do_move(board)
                    next_priority = \
                        manhattan_distance_2d((next_state.position_x, next_state.position_y), local_target_center)
                    heapq.heappush(local_queue, (next_priority, next_state))

    return {}


class BidirectionalPathFinder:

    def __init__(self, board: Board, search_depth: int, timeout: float):
        self.actionIntakeMaps = {}
        self.processingSet = set()
        self.board = board
        self.baseState = PlayerState(PlayerDirection.UP, -1, -1, -1, -1)
        self.pointsToProcess = []

        self.searchDepth = search_depth
        self.timeout = timeout

    def update(self, board: Board, player_state: PlayerState):
        self.baseState = player_state
        self.board = board
        self.processingSet = {(point[1], point[0]) for point in np.argwhere(np.array(self.board.cells) == 0).tolist()}
        self.__initialize_forward_actions(self.searchDepth)
        self.__aggregate_paths(self.timeout)

    def __initialize_forward_actions(self, depth: int):
        action_array = list(PlayerAction)
        argument_array = [(self.board, self.baseState, action, depth) for action in action_array]
        pool = mp.Pool(mp.cpu_count())
        result_array = pool.starmap(recursive_forward_search, argument_array)
        result = {}
        for idx in range(len(action_array)):
            result[action_array[idx]] = result_array[idx]
        self.actionIntakeMaps = result

    def __aggregate_paths(self, timeout: float):

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
        arguments = [(target_dict, share, self.board, self.actionIntakeMaps, timeout) for share in shares]
        result_array = pool.starmap(backward_aggregate_paths, arguments)

    def get_result_map(self) -> Dict[PlayerAction, np.ndarray]:
        result = {}
        for action, intake_map in self.actionIntakeMaps.items():
            array = np.zeros((self.board.height, self.board.width))
            for intake in intake_map.keys():
                array[intake.y, intake.x] = 1
            result[action] = array
        return result
