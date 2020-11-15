from game_data.player.PlayerState import PlayerState, PlayerDirection
from game_data.player.PlayerAction import PlayerAction
from game_data.game.Board import Board
import heapq
from multiprocessing import Process, Manager
import multiprocessing as mp
import numpy as np
from typing import Dict, Tuple
from collections import namedtuple
import math


Intake = namedtuple("Intake", "x y direction speed round_modulo")


class BidirectionalPathFinder:

    def __init__(self, width: int, height: int):
        self.cancelSets = [[set()] * width] * height
        self.pathEnds = [[None] * width] * height
        self.intakeMap = {}
        self.processingSet = set()
        self.board = Board(width, height)
        self.baseState = PlayerState(PlayerDirection.UP, -1, -1, -1, -1)
        self.pointsToProcess = []

    def update(self, board: Board, player_state: PlayerState):
        self.baseState = player_state
        self.board = board

        self.processingSet = {(point[1], point[0]) for point in np.argwhere(np.array(self.board.cells != 0)).tolist()}

        self.__initialize_forward_actions(5)

    def __initialize_forward_actions(self, depth: int):
        action_array = list(PlayerAction)
        argument_array = [(self.baseState, action, depth) for action in action_array]
        pool = mp.Pool(mp.cpu_count())
        result_array = pool.starmap(self.__recursive_forward_search, argument_array)
        result = {}
        for idx in range(len(action_array)):
            result[action_array[idx]] = result_array[idx]
        self.intakeMap = result

    def __recursive_forward_search(self, local_base_state: PlayerState, action: PlayerAction,
                                   max_depth: int, current_depth: int = 0) \
            -> Dict[Intake, PlayerState]:

        local_state_copy = local_base_state.copy()
        local_state_copy.do_action(action)
        local_next_state = local_state_copy.do_move()

        result = {}

        if local_next_state.verify_move(self.board):

            if current_depth <= max_depth:
                for action in PlayerAction:
                    result.update(self.__recursive_forward_search(local_next_state, action, max_depth,
                                                                  current_depth + 1))

            intake = Intake(local_next_state.position_x, local_next_state.position_y, local_next_state.direction,
                            local_next_state.speed, local_next_state.game_round % 6)
            result[intake] = local_next_state
            self.processingSet.discard((local_next_state.position_x, local_next_state.position_y))

        return result

    def __aggregate_paths(self):

        total_points = list(self.processingSet)

        # sort with angle
        total_points.sort(key=lambda x, y: (1 if y > 0 else -1) * math.acos(-x))

        # get shares of points to process
        shares = np.array_split(total_points, mp.cpu_count())

        for coreIdx in range(mp.cpu_count()):
            pass



    def __aggregate_paths_process(self):
        pass


    def __backward_search(self):
        pass


