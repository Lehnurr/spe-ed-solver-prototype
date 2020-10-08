from players.BasePlayer import BasePlayer
from simulation.player.PlayerAction import PlayerAction
import random
from analysis import full_range
from simulation.player.PlayerState import PlayerState
from simulation.player.PlayerState import PlayerDirection
from simulation.game.Board import Board
import numpy as np


class RandomFullRangePlayer(BasePlayer):

    def __init__(self):
        self.roundCounter = 0
        self.board = None
        self.playerState = None

    def handle_step(self, step_info, slice_viewer):

        self.roundCounter += 1
        own_player = step_info["players"][str(step_info["you"])]

        # init on first step info
        if self.roundCounter == 1:
            self.board = Board(step_info["width"], step_info["height"])
            self.playerState = PlayerState(PlayerDirection[own_player["direction"].upper()],
                                           own_player["speed"],
                                           own_player["x"],
                                           own_player["y"],
                                           self.roundCounter)

        # update cells
        self.board.cells = step_info["cells"]

        # calculate action
        full_range_result = full_range.calculate_ranges_for_player(self.board, self.playerState)
        path_options = list(full_range_result.values())
        if len(path_options) > 0:
            random_player_state_choice = random.choice(path_options)
            player_states = random_player_state_choice.previous + [random_player_state_choice]
            action = player_states[self.roundCounter-1].action

        # random action if no way to survive
        else:
            action = random.choice(list(PlayerAction))

        # add path options to viewer
        path_steps_array = np.zeros((step_info["height"], step_info["width"]))
        for key, value in full_range_result.items():
            path_steps_array[key] = value.game_round - self.roundCounter
        slice_viewer.add_data("full_range_steps", path_steps_array)

        # apply action to local model
        self.playerState.do_action(action)
        self.playerState = self.playerState.do_move()

        return action

    def get_slice_viewer_attributes(self):
        return ["full_range_steps"]
