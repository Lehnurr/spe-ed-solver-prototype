from analysis.full_range.next_range import calculate_next_states
from game_data.game.Board import Board
from game_data.player.PlayerState import PlayerState, PlayerAction
import numpy as np
from analysis.full_range import no_risk_full_range


def calculate_ranges_for_player_action(
        initial_state: PlayerState,
        player_action: PlayerAction,
        game_board: Board,
        enemy_probability: np.ndarray,
        enemy_min_steps: np.ndarray,
        lookup_round_count: int = -1) \
        -> np.ndarray:

    no_risk_full_range.calculate_ranges_for_player(game_board, initial_state)
    probability_result = np.zeros((game_board.height, game_board.width))

    initial_state = initial_state.copy()
    initial_state.do_action(player_action)
    first_next_state = initial_state.do_move()

    if not first_next_state.verify_move(game_board):
        return probability_result

    first_next_state.success_probability = \
        1 - max([enemy_probability[y, x] for x, y in first_next_state.steps_to_this_point
                 if enemy_min_steps[y, x] <= 1] + [0])

    probability_result[first_next_state.position_y, first_next_state.position_x] = first_next_state.success_probability

    full_range_result_data = {}
    next_states = [first_next_state]

    current_round = 0
    while len(next_states) > 0 and lookup_round_count != current_round:
        next_states = calculate_next_states(game_board, next_states, full_range_result_data)

        for state in next_states:
            state_max_risk = max([enemy_probability[y, x] for x, y in state.steps_to_this_point
                                  if enemy_min_steps[y, x] <= current_round + 2] + [0])

            state.success_probability = state.previous[-1].success_probability * (1 - state_max_risk)
            probability_result[state.position_y, state.position_x] = \
                max(state.success_probability, probability_result[state.position_y, state.position_x])

        current_round += 1

    return probability_result
