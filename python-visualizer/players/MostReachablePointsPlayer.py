from players.BasePlayer import BasePlayer
from game_data.player.PlayerAction import PlayerAction
import random
from analysis import full_range, risk_area
from analysis import probability_based_prediction
from analysis import safe_area_detection
from game_data.player.PlayerState import PlayerState
from game_data.player.PlayerState import PlayerDirection
from game_data.game.Board import Board
import numpy as np
import multiprocessing as mp


class MostReachablePointsPlayer(BasePlayer):

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

        # add safe_area sizes to viewer
        safe_areas, safe_area_labels = safe_area_detection.detect_safe_areas(np.array(self.board.cells))
        safe_area_sizes = np.zeros(safe_area_labels.shape)
        for y in range(safe_area_labels.shape[0]):
            for x in range(safe_area_labels.shape[1]):
                safe_area_idx = safe_area_labels[y, x]
                if safe_area_idx >= 0:
                    safe_area = safe_areas[safe_area_idx]
                    safe_area_sizes[y, x] = len(safe_area.points)
        slice_viewer.add_data("safe_area_sizes", safe_area_sizes, normalize=False)

        # add risk_area to viewer
        slice_viewer.add_data("risk_evaluation", risk_area.calculate_risk_areas(self.board), normalize=False)

        # apply threshold to probabilities
        enemy_probabilities[enemy_probabilities > 0.19] = 1
        enemy_probabilities[enemy_probabilities != 1] = 0

        # update board with probabilities
        self.board.cells = enemy_probabilities.tolist()

        # determine action with highest amount of reachable points
        player_action_array = [player_action for player_action in PlayerAction]
        pool = mp.Pool(mp.cpu_count())
        path_option_results = pool.map(self.get_full_range_path_options_for_action, player_action_array)
        pool.close()
        action_histogram = {player_action: len(path_option_results[player_action_array.index(player_action)])
                            for player_action in PlayerAction}
        action = max(action_histogram, key=action_histogram.get)

        # add path options to viewer
        path_steps_array = np.zeros((step_info["height"], step_info["width"]))
        path_options = path_option_results[player_action_array.index(action)]
        for option in path_options:
            x = option.position_x
            y = option.position_y
            current_value = path_steps_array[y, x]
            new_value = option.game_round - self.roundCounter
            path_steps_array[y, x] = new_value if current_value == 0 else min(current_value, new_value)

        slice_viewer.add_data("full_range_steps", path_steps_array)

        # apply action to local model
        self.playerState.do_action(action)
        self.playerState = self.playerState.do_move()

        return action

    def get_slice_viewer_attributes(self):
        return ["full_range_steps", "enemy_probability", "enemy_min_steps", "safe_area_sizes", "risk_evaluation"]

    def get_full_range_path_options_for_action(self, player_action: PlayerAction):
        player_state = self.playerState.copy()
        player_state.do_action(player_action)
        player_state = player_state.do_move()
        if not player_state.verify_move(self.board):
            return []
        full_range_result = full_range.calculate_ranges_for_player(self.board, player_state)
        path_options = [state
                        for directions in full_range_result.values()
                        for speeds in directions.values()
                        for state in speeds.values()]
        return path_options
