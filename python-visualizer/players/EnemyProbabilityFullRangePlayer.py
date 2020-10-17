from players.BasePlayer import BasePlayer
from game_data.player.PlayerAction import PlayerAction
import random
from analysis import full_range, risk_area
from analysis import probability_based_prediction
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

        # calculate enemy prediction
        enemy_probabilities, enemy_min_steps = \
            probability_based_prediction.calculate_probabilities_for_players(self.board, enemy_player_states, depth=7)

        # add enemy prediction to viewer
        slice_viewer.add_data("enemy_probability", enemy_probabilities, normalize=False)
        slice_viewer.add_data("enemy_min_steps", enemy_min_steps, normalize=True)

        # add risk_area to viewer
        slice_viewer.add_data("risk_evaluation", risk_area.calculate_risk_areas(self.board), normalize=False)

        # apply threshold to probabilities
        enemy_probabilities[enemy_probabilities > 0.19] = 1
        enemy_probabilities[enemy_probabilities != 1] = 0

        # update board with probabilities
        self.board.cells = enemy_probabilities.tolist()

        # calculate action
        full_range_result = full_range.calculate_ranges_for_player(self.board, self.playerState)
        path_options = list(full_range_result.values())
        if len(path_options) > 0:

            # determine action with highest amount of reachable points
            action_histogram = {player_action: 0 for player_action in PlayerAction}
            for path_option in path_options:
                player_states = path_option.previous + [path_option]
                path_action = player_states[self.roundCounter - 1].action
                action_histogram[path_action] += 1
            action = max(action_histogram, key=action_histogram.get)

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
        return ["full_range_steps", "enemy_probability", "enemy_min_steps", "risk_evaluation"]
