from simulation.player import PlayerAction
from simulation.spe_ed_localservice import LocalGameService


print("start Game")
game = LocalGameService(10, 5, 2)
print(f'Init State: {game.cells}')

for round_number in range(5):
    print(f'Do {round_number}. Round')
    game.do_action(1, PlayerAction.TURN_LEFT)
    game.do_action(2, PlayerAction.CHANGE_NOTHING)
    game.next_round()
    print(f'Next State: {game.cells}')

