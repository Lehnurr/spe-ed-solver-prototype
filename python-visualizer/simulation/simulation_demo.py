import time

from simulation.player import PlayerAction
from simulation.spe_ed_localservice import LocalGameService


def log_round_data(json_data: str):
    print(json_data)


def player_one_do_action(json_data: str):
    time.sleep(2)
    game.do_action(1, PlayerAction.CHANGE_NOTHING)


def player_two_do_action(json_data: str):
    time.sleep(2)
    game.do_action(2, PlayerAction.TURN_RIGHT)


print("start Game")
game = LocalGameService(5, 5, 2)
game.on_round_start += log_round_data
game.on_round_start += player_one_do_action
game.on_round_start += player_two_do_action
game.start()



