from players.BasePlayer import BasePlayer
import random


class RandomPlayer(BasePlayer):

    def __init__(self):
        pass

    def handle_step(self, step_info):
        print("<", step_info)
        own_player = step_info["players"][str(step_info["you"])]

        valid_actions = ["turn_left", "turn_right", "change_nothing"]
        if own_player["speed"] < 10:
            valid_actions += ["speed_up"]
        if own_player["speed"] > 1:
            valid_actions += ["slow_down"]
        action = random.choice(valid_actions)
        return action

    def get_slice_viewer_attributes(self):
        return []
