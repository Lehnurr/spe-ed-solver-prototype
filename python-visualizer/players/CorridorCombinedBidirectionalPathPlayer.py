from analysis.area_detection.safe_and_risk_area_combination import get_risk_evaluated_safe_areas
from players.BasePlayer import BasePlayer
from game_data.player.PlayerAction import PlayerAction
from analysis.bidirectional_path_finding.BidirectionalPathFinder import BidirectionalPathFinder
from analysis import probability_based_prediction
from analysis.area_detection import risk_area_calculation
from analysis.fill import corridor_fill_detection
from game_data.player.PlayerState import PlayerState
from game_data.player.PlayerState import PlayerDirection
from game_data.game.Board import Board
import numpy as np
import multiprocessing as mp


class CorridorCombinedBidirectionalPathPlayer(BasePlayer):

    def __init__(self):

        self.REACHABLE_POINT_WEIGHT = 1
        self.FILL_WEIGHT = 0.2
        self.SLOW_FORCE_WEIGHT = 0.1

        self.roundCounter = 0
        self.board = None
        self.playerState = None
        self.pathFinder = None

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
            self.pathFinder = BidirectionalPathFinder(self.board, 5, 2)

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
        safe_areas, safe_area_labels = get_risk_evaluated_safe_areas(self.board)
        safe_area_sizes = np.zeros(safe_area_labels.shape)
        for area in safe_areas:
            for point in area.points:
                safe_area_sizes[point[1], point[0]] = area.risk

        slice_viewer.add_data("safe_area_sizes", safe_area_sizes, normalize=False)

        # add risk_area to viewer
        slice_viewer.add_data("risk_evaluation", risk_area_calculation.calculate_risk_areas(self.board), normalize=False)

        # get path finder results for each possible action
        self.pathFinder.update(self.board, self.playerState)
        path_finder_result_map = self.pathFinder.get_result_map()

        # calculate reachable points for full range results
        max_reachable_points_value = \
            max(max([np.sum(result) for result in path_finder_result_map.values()]), 1)
        reachable_points = {player_action: np.sum(result) / max_reachable_points_value
                            for player_action, result in path_finder_result_map.items()}

        # calculate action distribution for full range results
        fill_distribution = corridor_fill_detection.determine_fill_values(self.playerState, self.board)

        # build slow down force
        slow_force = {player_action: 0. for player_action in PlayerAction}
        slow_base_state = self.playerState.copy()
        slow_base_state.do_action(PlayerAction.SLOW_DOWN)
        slow_next_state = slow_base_state.do_move()
        if slow_next_state.verify_move(self.board):
            slow_force[PlayerAction.SLOW_DOWN] = 1.

        # calculate weighted evaluation for each possible action
        print(f"\t\t\treachable:\t\t{reachable_points}")
        print(f"\t\t\tfill:\t\t\t{fill_distribution}")
        print(f"\t\t\tslow:\t\t\t{slow_force}")
        weighted_action_evaluation = {action:
                                      reachable_points[action] * self.REACHABLE_POINT_WEIGHT +
                                      fill_distribution[action] * self.FILL_WEIGHT +
                                      slow_force[action] * self.SLOW_FORCE_WEIGHT
                                      for action in PlayerAction}
        print(f"\t\t\tevaluation:\t\t{weighted_action_evaluation}")

        # chose action based of highest value
        action = max(weighted_action_evaluation, key=weighted_action_evaluation.get)

        # add reachable points to viewer
        selected_reachable_points = path_finder_result_map[action]
        slice_viewer.add_data("full_range_probability", selected_reachable_points, normalize=False)

        # apply action to local model
        self.playerState.do_action(action)
        self.playerState = self.playerState.do_move()

        return action

    def get_slice_viewer_attributes(self):
        return ["full_range_probability", "enemy_probability", "enemy_min_steps", "safe_area_sizes", "risk_evaluation"]
