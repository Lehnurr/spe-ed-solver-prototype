from players.BasePlayer import BasePlayer
from game_data.player.PlayerAction import PlayerAction
import random


class RandomPlayer(BasePlayer):

    def __init__(self):
        pass

    def handle_step(self, step_info, slice_viewer):
        print("<", step_info)
        own_player = step_info["players"][str(step_info["you"])]

        valid_actions = [PlayerAction.TURN_LEFT, PlayerAction.TURN_RIGHT, PlayerAction.CHANGE_NOTHING]
        if own_player["speed"] < 10:
            valid_actions += [PlayerAction.SPEED_UP]
        if own_player["speed"] > 1:
            valid_actions += [PlayerAction.SLOW_DOWN]
        action = random.choice(valid_actions)
        return action

    def get_slice_viewer_attributes(self):
        return []
