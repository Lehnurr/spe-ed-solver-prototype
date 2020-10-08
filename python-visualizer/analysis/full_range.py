from datetime import datetime

from simulation.game.Board import Board
from simulation.player.PlayerAction import PlayerAction
from simulation.player.PlayerState import PlayerDirection, PlayerState


def calculate_ranges_for_player(board: Board, initial_state: PlayerState):
    print(f'start: {datetime.now()}')
    result_data = {}

    next_states = [initial_state]
    while len(next_states) > 0:
        possible_next_states = list(do_actions(next_states))
        next_states = []
        for state in possible_next_states:
            if not verify_state(board, state):
                continue  # remove state, (collision)

            if result_data.get((state.position_x, state.position_y), False):
                continue  # remove state, (there's a better solution)

            result_data[(state.position_x, state.position_y)] = state
            next_states.append(state)

    print(f'end: {datetime.now()}')
    print(f'found {len(result_data)} elements')
    return result_data


def verify_state(board: Board, state: PlayerState) -> bool:
    # check for speed conditions
    # check if new pos is on board
    if not state.state_is_valid(board):
        return False

    # check for collisions with other players
    # check for collisions with myself
    for step in state.steps_to_this_point:
        if not board.point_is_available(step[0], step[1]) or state.collided_with_own_line:
            return False

    return True


def do_actions(state_list):
    for state in state_list:
        for action in PlayerAction:
            copy = state.copy()
            copy.do_action(action)
            yield copy.do_move()


if __name__ == "__main__":
    calculate_ranges_for_player(Board(10, 10), PlayerState(PlayerDirection.DOWN, 1, 4, 4, 1))
