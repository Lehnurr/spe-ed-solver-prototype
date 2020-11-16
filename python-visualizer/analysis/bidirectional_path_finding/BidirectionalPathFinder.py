from game_data.player.PlayerState import PlayerState, PlayerDirection
from game_data.player.PlayerAction import PlayerAction
from game_data.game.Board import Board
import heapq
from multiprocessing import Process, Manager
import multiprocessing as mp
import numpy as np
from typing import Dict, Tuple, Set
from collections import namedtuple
import math
import time


Intake = namedtuple("Intake", "x y direction speed round_modulo")


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


def backward_aggregate_paths(base_state: PlayerState, share: list, timeout: float) -> Dict[Intake, PlayerState]:

    process_priority_queue = []
    for x, y in share:
        heapq.heappush(process_priority_queue,
                       (abs(x - base_state.position_x) + abs(y - base_state.position_y), x, y))

    start_time = time.time()
    while time.time() - start_time < timeout:
        pass

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

        # sort by angle
        total_points.sort(key=lambda p: math.atan2(p[1] - self.baseState.position_y, p[0] - self.baseState.position_x))

        # get shares of points to process
        shares = np.array_split(total_points, mp.cpu_count())

        pool = mp.Pool(mp.cpu_count())
        arguments = [(self.baseState, share, timeout) for share in shares]
        result_array = pool.starmap(backward_aggregate_paths, arguments)

    def get_result_map(self) -> Dict[PlayerAction, np.ndarray]:
        result = {}
        for action, intake_map in self.actionIntakeMaps.items():
            array = np.zeros((self.board.height, self.board.width))
            for intake in intake_map.keys():
                array[intake.y, intake.x] = 1
            result[action] = array
        return result
