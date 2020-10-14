from players.BasePlayer import BasePlayer
from game_data.player.PlayerAction import PlayerAction
import random
from analysis import full_range
from analysis import player_location_probability
from game_data.player.PlayerState import PlayerState
from game_data.player.PlayerState import PlayerDirection
from game_data.game.Board import Board
import numpy as np


class EnemyProbabilityFullRangePlayer(BasePlayer):

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

        # build enemy player states
        enemy_player_states = []
        for player_id, player in step_info["players"].items():
            if str(step_info["you"]) != player_id and player["active"]:
                enemy_player_states.append(
                    PlayerState(
                        PlayerDirection[player["direction"].upper()],
                        player["speed"],
                        player["x"],
                        player["y"],
                        self.roundCounter))

        # calculate enemy probabilities
        enemy_probabilities = \
            player_location_probability.calculate_probabilities_for_players(self.board, enemy_player_states,
                                                                            depth=5, invalid_move_weight=0)

        # add probability to viewer
        slice_viewer.add_data("enemy_probability", enemy_probabilities, normalize=False)

        # apply threshold to probabilities
        enemy_probabilities[enemy_probabilities > 0.4] = 1

        # update board with probabilities
        self.board.cells = enemy_probabilities.tolist()

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
            path_steps_array[key[1], key[0]] = value.game_round - self.roundCounter
        slice_viewer.add_data("full_range_steps", path_steps_array)

        # apply action to local model
        self.playerState.do_action(action)
        self.playerState = self.playerState.do_move()

        return action

    def get_slice_viewer_attributes(self):
        return ["full_range_steps", "enemy_probability"]
