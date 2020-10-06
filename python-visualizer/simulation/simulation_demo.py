import time

from simulation.player.player_action import PlayerAction
from simulation.spe_ed_localservice import LocalGameService


def log_round_data(json_data: str):
    print(json_data)


# Code for Player#1-Actions
def player_one_do_action(json_data: str):
    game.do_action(1, PlayerAction.CHANGE_NOTHING)


# Code for Player#2-Actions
def player_two_do_action(json_data: str):
    game.do_action(2, PlayerAction.TURN_RIGHT)


# Init Game
print("start Game")
game = LocalGameService(10, 10, 2)
game.on_round_start += log_round_data
game.on_round_start += player_one_do_action
game.on_round_start += player_two_do_action
game.start()
