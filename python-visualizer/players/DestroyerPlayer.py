from analysis.area_detection.safe_and_risk_area_combination import get_risk_evaluated_safe_areas
from analysis.full_range import no_risk_full_range
from players.BasePlayer import BasePlayer
from game_data.player.PlayerAction import PlayerAction
import random
from analysis import probability_based_prediction
from analysis.area_detection import safe_area_detection, risk_area_calculation
from game_data.player.PlayerState import PlayerState
from game_data.player.PlayerState import PlayerDirection
from game_data.game.Board import Board
import numpy as np


class DestroyerPlayer(BasePlayer):

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
        safe_areas, safe_area_labels = get_risk_evaluated_safe_areas(self.board)
        safe_area_sizes = np.zeros(safe_area_labels.shape)
        for area in safe_areas:
            for point in area.points:
                safe_area_sizes[point[1], point[0]] = area.risk

        slice_viewer.add_data("safe_area_sizes", safe_area_sizes, normalize=False)

        # add risk_area to viewer
        slice_viewer.add_data("risk_evaluation", risk_area_calculation.calculate_risk_areas(self.board), normalize=False)

        # apply threshold to probabilities
        enemy_probabilities[enemy_probabilities > 0.19] = 1
        enemy_probabilities[enemy_probabilities != 1] = 0

        # update board with probabilities
        self.board.cells = enemy_probabilities.tolist()

        # calculate action
        full_range_result = no_risk_full_range.calculate_ranges_for_player(self.board, self.playerState)
        path_options = [state
                        for directions in full_range_result.values()
                        for speeds in directions.values()
                        for state in speeds.values()]

        #TODO: consider moving to a line to split the area, not to the farest border
        if len(path_options) > 0:
            # determine action with highest amount of reachable points as fallback
            action_histogram = {player_action: 0 for player_action in PlayerAction}
            for path_option in path_options:
                player_states = path_option.previous + [path_option]
                path_action = player_states[self.roundCounter - 1].action
                action_histogram[path_action] += 1
            action = max(action_histogram, key=action_histogram.get)

            x_pos = self.playerState.position_x
            y_pos = self.playerState.position_y
            if len(safe_areas) == 1:
                # if there is only one safe_area: destroy it by moving to the most distance border
                area = safe_areas[0]
                reachable_states = [state for state in path_options if state.get_position_tuple() in area.points]
                most_distance_state = max(reachable_states,
                                          key=lambda s: abs(abs(s.position_x) - abs(x_pos)) + abs(
                                              abs(s.position_y) - abs(y_pos)))
                action = (most_distance_state.previous + [most_distance_state])[self.roundCounter - 1].action
            else:
                # order safe areas by risk ascending
                sorted_safe_areas = sorted(safe_areas, key=lambda a: a.risk)
                for area in sorted_safe_areas:
                    if (x_pos + 1, y_pos) in area.points \
                            or (x_pos, y_pos + 1) in area.points \
                            or (x_pos - 1, y_pos) in area.points \
                            or (x_pos, y_pos - 1) in area.points:
                        # already in the area: split it by moving to the most distance border
                        reachable_states = [state for state in path_options if
                                            state.get_position_tuple() in area.points]
                        most_distance_state = max(reachable_states,
                                                  key=lambda s: abs(abs(s.position_x) - abs(x_pos)) + abs(
                                                      abs(s.position_y) - abs(y_pos)))
                        action = (most_distance_state.previous + [most_distance_state])[self.roundCounter - 1].action
                    elif len([state for state in path_options if state.get_position_tuple() in area.points]) > 0:
                        # can reach, go there
                        states = [state for state in path_options if state.get_position_tuple() in area.points]
                        # use the shortest path
                        state = min(states, key=lambda s: s.game_round)
                        action = (state.previous + [state])[self.roundCounter - 1].action
                    else:
                        # this is the last safe_area: split it by moving to the most distance border
                        reachable_states = [state for state in path_options if
                                            state.get_position_tuple() in area.points]
                        if len(reachable_states) > 0:
                            most_distance_state = max(reachable_states,
                                                      key=lambda s: abs(abs(s.position_x) - abs(x_pos)) + abs(
                                                          abs(s.position_y) - abs(y_pos)))
                            action = (most_distance_state.previous + [most_distance_state])[self.roundCounter - 1].action
        # random action if no way to survive
        else:
            action = random.choice(list(PlayerAction))

        # add path options to viewer
        path_steps_array = np.zeros((step_info["height"], step_info["width"]))
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
