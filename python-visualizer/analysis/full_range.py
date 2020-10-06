from simulation.game.Board import Board
from simulation.player.PlayerAction import PlayerAction
from simulation.player.PlayerState import PlayerDirection, PlayerState


def calculate_ranges_for_player(board: Board, initial_state: PlayerState):
    # Transform Cells to result_data
    transformer = {-1: -1, 0: {PlayerDirection.UP: None,
                               PlayerDirection.RIGHT: None,
                               PlayerDirection.DOWN: None,
                               PlayerDirection.LEFT: None,
                               }, }
    result_data = [[transformer.get(cell, -1) for cell in row] for row in board]

    next_states = [initial_state]
    while len(next_states) > 0:
        next_states = do_actions(next_states)
        good_next_states = []
        for state in next_states:
            if not verify_state(board, state):
                continue  # remove state, (collision)

            if result_data[state.position_y][state.position_x].get(state.direction) is not None:
                continue  # remove state, (there's a better solution)

            result_data[state.position_y][state.position_x][state.direction] = state
            good_next_states.append(state)

        next_states = good_next_states


def verify_state(board: Board, state: PlayerState) -> bool:
    # check for collisions with other players
    # check if new pos is on board
    for step in state.steps_to_this_point:
        if not board.point_is_available(step[0], step[1]):
            return False

    # TODO: check for collisions with myself

    return True


def do_actions(state_list):
    for state in state_list:
        for action in PlayerAction:
            copy = state.copy()
            copy.do_action(action)
            copy.do_move()
            yield copy


calculate_ranges_for_player(Board(10, 10), PlayerState(PlayerDirection.LEFT, 1, 0, 0, 1))

# später auch speed + und jump
# felder gewichten mit player speed und einene radius setzen
# von vorrunde üpbernehmen
# an jedem feld speiochern wpo ich hi komme
# multithreading
