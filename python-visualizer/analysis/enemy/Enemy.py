from math import sqrt
from statistics import median

from game_data.player.Player import Player
from game_data.player.PlayerAction import PlayerAction
from game_data.player.PlayerState import PlayerState, PlayerDirection


class Enemy(Player):
    def __init__(self, player_id: int, direction: PlayerDirection, speed: int, x_position: int, y_position: int):
        super().__init__(player_id, PlayerState(direction, speed, x_position, y_position))
        self.min_speed = speed
        self.max_speed = speed
        self.avg_speed = speed
        self.walked_cells = 1
        self.jumped_cells = 1
        self.radius = 0.5
        self.center_cell_per_round = [(x_position, y_position)]
        self.center_cell_differences = []
        self.median_per_round = [(x_position, y_position)]
        self.avg_distance_to_median = 0

    def update(self, step_info):
        # compute last action
        self.next_action = PlayerAction.CHANGE_NOTHING
        if step_info["speed"] > self.current_state.speed:
            self.next_action = PlayerAction.SPEED_UP
        elif step_info["speed"] < self.current_state.speed:
            self.next_action = PlayerAction.SLOW_DOWN
        elif self.current_state.direction.turn(PlayerAction.TURN_LEFT).name.lower() == step_info["direction"]:
            self.next_action = PlayerAction.TURN_LEFT
        elif self.current_state.direction.turn(PlayerAction.TURN_RIGHT).name.lower() == step_info["direction"]:
            self.next_action = PlayerAction.TURN_RIGHT

        # do last action
        self.do_action_and_move()

        # Recalculate the speed-behavior (min, max, avg)
        current_speed = self.current_state.speed
        self.min_speed = min(current_speed, self.min_speed)
        self.max_speed = max(current_speed, self.max_speed)
        number_of_rounds = self.current_state.game_round
        self.avg_speed = (self.avg_speed * number_of_rounds + current_speed) / (number_of_rounds + 1)

        # Recalculate the Number of passed cells (incl. & excl. jumped over cells)
        last_walked_cells = len(self.current_state.steps_to_this_point)
        self.walked_cells += last_walked_cells
        self.jumped_cells += current_speed - last_walked_cells

        # get all passed positions
        all_positions = self.current_state.all_steps.keys()

        # Calculate the new Center-Cell
        # This is the center of a player-rectangle (limited by the extreme-points in each direction)
        top = min(all_positions, key=lambda p: p[1])[1]
        left = min(all_positions, key=lambda p: p[0])[0]
        right = max(all_positions, key=lambda p: p[0])[0]
        bottom = max(all_positions, key=lambda p: p[1])[1]
        center_x = (top + bottom) / 2
        center_y = (left + right) / 2
        self.center_cell_per_round.append((center_x, center_y))

        # Calculate the new Center-Cell-Difference
        # for this operation at least 2 calculated center cells are required (this is always the case here)
        x_difference = self.center_cell_per_round[-2][0] - center_x
        y_difference = self.center_cell_per_round[-2][1] - center_y
        self.center_cell_differences.append((x_difference, y_difference))

        # Recalculate the radius of the passed cells
        # This is the distance from the center to the top-left-player-rectangle-corner
        self.radius = sqrt((left - center_x)**2 + (top - center_y)**2)

        # Calculate the new median
        median_x = median(pos[0] for pos in all_positions)
        median_y = median(pos[1] for pos in all_positions)
        self.median_per_round.append((median_x, median_y))
        # TODO: dont use all_positions; only back to the round where the center cell difference is not too high

        # Recalculate the average distance to the median
        x_pos = self.current_state.position_x
        y_pos = self.current_state.position_y
        median_distance = sqrt((median_x - x_pos)**2 + (median_y - y_pos)**2)
        old_avg_distance = self.avg_distance_to_median
        self.avg_distance_to_median = (old_avg_distance * (number_of_rounds - 1) + median_distance) / number_of_rounds

    def recalculate_aggressiveness(self, enemies_states):
        pass
        # TODO: recalculate_aggressiveness:

        # - airline to the nearest player (avg, min, max, differences for all rounds)
        #    also consider a weighted air line (to estimate the distance in rounds)
        # - Number of taken / prevent potential collisions
        #   collision means that in at least one case at least one player would die in the next x rounds (default x = 2)

        # - Maybe evaluate movement in risk areas
        #   (if they often move in high-risk areas, they are willing to take a risk, or stupid)
