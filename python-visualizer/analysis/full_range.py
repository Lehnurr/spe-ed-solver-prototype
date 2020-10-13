from datetime import datetime

from game_data.game.Board import Board
from game_data.player.PlayerAction import PlayerAction
from game_data.player.PlayerState import PlayerDirection, PlayerState


def calculate_ranges_for_player(board: Board, initial_state: PlayerState, lookup_round_count: int = -1):
    result_data = {}

    next_states = [initial_state]
    while len(next_states) > 0 and lookup_round_count != 0:
        possible_next_states = list(do_actions(next_states))
        next_states = []
        for state in possible_next_states:
            if not state.verify_move(board):
                continue  # remove state, (collision)

            if result_data.get((state.position_x, state.position_y), False):
                continue  # remove state, (there's a better solution)

            result_data[(state.position_x, state.position_y)] = state
            next_states.append(state)
        lookup_round_count -= 1

    return result_data


def do_actions(state_list):
    for state in state_list:
        for action in PlayerAction:
            copy = state.copy()
            copy.do_action(action)
            yield copy.do_move()


if __name__ == "__main__":
    calculate_ranges_for_player(Board(10, 10), PlayerState(PlayerDirection.DOWN, 1, 4, 4, 1))
