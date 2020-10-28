from game_data.player.Player import Player
from game_data.player.PlayerAction import PlayerAction
from game_data.player.PlayerState import PlayerState, PlayerDirection


class Enemy(Player):
    def __init__(self, player_id: int, direction: PlayerDirection, speed: int, x_position: int, y_position: int):
        super().__init__(player_id, PlayerState(direction, speed, x_position, y_position))

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

    def recalculate_aggressiveness(self, enemies_states):
        pass
        # recalculate_aggressiveness:
        # - speed-behavior (avg, min, max) & Number of passed cells (incl. & excl. jumped over cells)
        # - radius of the passed cells / span of the passed cells

        # - airline to the nearest player (avg, min, max, differences for all rounds)
        #    also consider a weighted air line (to estimate the distance in rounds)
        # - Number of taken / prevent potential collisions
        #   collision means that in at least one case at least one player would die in the next x rounds (default x = 2)

        # - Evaluate movement in risk areas
        #   (if they often move in high-risk areas, they are willing to take a risk, or stupid)
