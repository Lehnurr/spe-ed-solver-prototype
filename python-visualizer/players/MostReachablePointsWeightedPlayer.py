from players.BasePlayer import BasePlayer
from game_data.player.PlayerAction import PlayerAction
from analysis import risk_area
from analysis import probability_based_prediction
from analysis import safe_area_detection
from game_data.player.PlayerState import PlayerState
from game_data.player.PlayerState import PlayerDirection
from game_data.game.Board import Board
import numpy as np
import multiprocessing as mp
from analysis import reachable_points
import time


class MostReachablePointsWeightedPlayer(BasePlayer):

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

        start_time = time.time()
        # add risk_area to viewer
        slice_viewer.add_data("risk_evaluation", risk_area.calculate_risk_areas(self.board), normalize=False)

        # determine amount of reachable points for each action
        pool_input_array = [(player_action, enemy_probabilities, enemy_min_steps) for player_action in PlayerAction]
        pool = mp.Pool(mp.cpu_count())
        weighted_points_results = pool.starmap(self.get_weighted_points_for_action, pool_input_array)
        pool.close()
        action_rating = {}
        action_weight_mapping = {}
        for idx, weighted_points_result in enumerate(weighted_points_results):
            action_weight_mapping[pool_input_array[idx][0]] = weighted_points_result
            action_rating[pool_input_array[idx][0]] = np.sum(weighted_points_result)

        # chose action based of highest value
        action = max(action_rating, key=action_rating.get)

        # add weighted points to viewer
        slice_viewer.add_data("weighted_points", action_weight_mapping[action])

        # apply action to local model
        self.playerState.do_action(action)
        self.playerState = self.playerState.do_move()

        return action

    def get_slice_viewer_attributes(self):
        return ["weighted_points", "enemy_probability", "enemy_min_steps", "safe_area_sizes", "risk_evaluation"]

    def get_weighted_points_for_action(self,
                                       player_action: PlayerAction,
                                       probabilities: np.ndarray,
                                       min_steps: np.ndarray):
        player_state = self.playerState.copy()
        player_state.do_action(player_action)
        player_state = player_state.do_move()
        full_range_result = \
            reachable_points.calculate_reachable_points_weighted(player_state, 1, self.board, probabilities, min_steps, 1)
        return full_range_result
