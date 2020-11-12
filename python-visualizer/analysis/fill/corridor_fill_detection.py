import numpy as np
from analysis.fill.CorridorDetection import CorridorDetection
from game_data.player.PlayerState import PlayerState
from game_data.player.PlayerAction import PlayerAction
from game_data.game.Board import Board
from typing import Dict
from typing import Tuple


__CORRIDOR_DETECTION = CorridorDetection()


def determine_fill_values(
        player_state: PlayerState,
        board: Board,
        search_length: int) -> Dict[PlayerAction, float]:

    input_array = np.array(board.cells)

    corridor_map = __CORRIDOR_DETECTION.get_corridor_map(input_array)

    return None