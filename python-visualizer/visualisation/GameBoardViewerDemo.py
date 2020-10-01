
from visualisation import GameBoardViewer

WIDTH = 32
HEIGHT = 32

field = [[0 for x in range(WIDTH)] for y in range(HEIGHT)]

aGameBoardViewer = GameBoardViewer.GameBoardViewer(WIDTH, HEIGHT)

aGameBoardViewer.add_game_state(field)
aGameBoardViewer.add_game_state(field)
aGameBoardViewer.add_game_state(field)
aGameBoardViewer.add_game_state(field)
aGameBoardViewer.add_game_state(field)

aGameBoardViewer.plot_game_states()

