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
        self.max_radius = 0.5
        self.gradients_per_round = [(x_position, y_position)]
        # TODO: Add calculation for gradient differences and overall-time Gradient

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

        # TODO: Recalculate the radius of the passed cells

    def recalculate_aggressiveness(self, enemies_states):
        pass
        # TODO: recalculate_aggressiveness:

        # - airline to the nearest player (avg, min, max, differences for all rounds)
        #    also consider a weighted air line (to estimate the distance in rounds)
        # - Number of taken / prevent potential collisions
        #   collision means that in at least one case at least one player would die in the next x rounds (default x = 2)

        # - Maybe evaluate movement in risk areas
        #   (if they often move in high-risk areas, they are willing to take a risk, or stupid)
