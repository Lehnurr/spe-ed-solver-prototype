import matplotlib.pyplot as plt
import numpy as np
from visualisation import SliceViewer


GAME_BOARD_BACKGROUND_COLOUR = (255, 255, 255)
GAME_BOARD_ERROR_COLOUR = (0, 0, 0)
GAME_BOARD_PLAYER_COLOURS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]


class GameBoardViewer:

    def __init__(self, game_width, game_height):
        self.gameWidth = game_width
        self.gameHeight = game_height
        self.gameStates = []

    def add_game_state(self, game_board_content):
        assert (len(game_board_content) == self.gameHeight)
        assert (len(game_board_content[0]) == self.gameWidth)

        current_state = np.zeros((self.gameHeight, self.gameWidth, 3), dtype=np.uint8)
        pixels = 0
        for rowIdx, row in enumerate(game_board_content):
            for colIdx, elem in enumerate(row):

                if elem > 0:
                    pixels += 1
                    current_state[rowIdx, colIdx] = GAME_BOARD_PLAYER_COLOURS[elem - 1]
                elif elem == -1:
                    current_state[rowIdx, colIdx] = GAME_BOARD_ERROR_COLOUR
                else:
                    current_state[rowIdx, colIdx] = GAME_BOARD_BACKGROUND_COLOUR

        print(f"pixels:\t{pixels}")
        self.gameStates.append(current_state)

    def plot_game_states(self):
        slices = np.array(self.gameStates)
        SliceViewer.show_numpy_slice_viewer(slices)
