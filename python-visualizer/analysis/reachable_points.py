import time
from game_data.game.Board import Board
from game_data.player.PlayerState import PlayerState, PlayerAction
import numpy as np
from threading import Thread


class ReachablePointsCalculation:

    def __init__(self, initial_player_state: PlayerState, board: Board):
        self.__reachablePoints = np.zeros((board.height, board.width))
        self.__queue = [initial_player_state]
        self.__board = board
        self.__running = False
        self.__thread = Thread(target=self.__run, args=())
        self.__thread.start()

    def __run(self):
        if not self.__running:
            self.__running = True
            while True:
                if len(self.__queue) == 0 or not self.__running:
                    break
                local_base_state = self.__queue.pop(0)
                for action in PlayerAction:
                    state_copy = local_base_state.copy()
                    state_copy.do_action(action)
                    state_variation = state_copy.do_move()
                    if state_variation.verify_move(self.__board):
                        self.__queue.append(state_variation)
                        for x, y in state_variation.steps_to_this_point:
                            self.__reachablePoints[y, x] = 1

    def stop(self):
        self.__running = False
        self.__thread.join()

    def get_result(self):
        return self.__reachablePoints.copy()


def calculate_reachable_points(initial_player_state: PlayerState, board: Board, seconds_to_spend: int) -> np.ndarray:

    calc = ReachablePointsCalculation(initial_player_state, board)
    time.sleep(seconds_to_spend)
    calc.stop()
    res = calc.get_result()

    return res
