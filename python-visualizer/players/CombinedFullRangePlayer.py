from analysis.area_detection.safe_and_risk_area_combination import get_risk_evaluated_safe_areas
from players.BasePlayer import BasePlayer
from game_data.player.PlayerAction import PlayerAction
from analysis.full_range import no_risk_full_range
from analysis import probability_based_prediction
from analysis.area_detection import safe_area_cutting_detection, risk_area_calculation
from game_data.player.PlayerState import PlayerState
from game_data.player.PlayerState import PlayerDirection
from game_data.game.Board import Board
import numpy as np
import multiprocessing as mp
import time


class CombinedFullRangePlayer(BasePlayer):

    def __init__(self):

        self.PROBABILITY_WEIGHT = 1
        self.REACHABLE_POINT_WEIGHT = 1
        self.DESTRUCTION_WEIGHT = 0.2

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

        # calculate probabilities for next actions
        next_action_success_probability = {action: 0 for action in PlayerAction}
        probabilities_in_next_step = np.copy(enemy_probabilities)
        probabilities_in_next_step[enemy_min_steps != 1] = 0
        for action in PlayerAction:
            current_player_state = self.playerState.copy()
            current_player_state.do_action(action)
            possible_next_player_state = current_player_state.do_move()
            if possible_next_player_state.verify_move(self.board):
                max_enemy_probability = 0
                for x, y in possible_next_player_state.steps_to_this_point:
                    max_enemy_probability = max(probabilities_in_next_step[y, x], max_enemy_probability)
                next_action_success_probability[action] = 1 - max_enemy_probability

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

        # get full range result for each possible action
        player_action_array = [player_action for player_action in PlayerAction]
        pool = mp.Pool(mp.cpu_count())
        path_option_results = pool.map(self.get_full_range_path_options_for_action, player_action_array)
        pool.close()
        full_range_results = {player_action: path_option_results[player_action_array.index(player_action)]
                              for player_action in PlayerAction}

        # calculate reachable points for full range results
        max_reachable_points = max(max([len(paths) for paths in full_range_results.values()]), 1)
        reachable_points = {player_action: len(paths) / max_reachable_points
                            for player_action, paths in full_range_results.items()}

        # calculate action distribution for full range results
        cutting_distribution = safe_area_cutting_detection.determine_cutting_values(self.playerState, self.board, 10)
        destruction_distribution = {action: 1 - cutting_value for action, cutting_value in cutting_distribution.items()}

        # calculate weighted evaluation for each possible action
        print(f"\t\t\tprobability:\t{next_action_success_probability}")
        print(f"\t\t\treachable:\t\t{reachable_points}")
        print(f"\t\t\tdestruction:\t{destruction_distribution}")
        weighted_action_evaluation = {action:
                                      next_action_success_probability[action] * self.PROBABILITY_WEIGHT +
                                      reachable_points[action] * self.REACHABLE_POINT_WEIGHT +
                                      destruction_distribution[action] * self.DESTRUCTION_WEIGHT
                                      for action in PlayerAction}
        print(f"\t\t\tevaluation:\t\t{weighted_action_evaluation}")

        # chose action based of highest value
        action = max(weighted_action_evaluation, key=weighted_action_evaluation.get)

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
        full_range_result = no_risk_full_range.calculate_ranges_for_player(self.board, player_state)
        path_options = [state
                        for directions in full_range_result.values()
                        for speeds in directions.values()
                        for state in speeds.values()]
        return path_options
