from players.RandomPlayer import RandomPlayer
from players.RandomFullRangePlayer import RandomFullRangePlayer
from management.PlayerController import PlayerController


def get_player_controllers(selected_player_types, player_count):
    player_instances = []

    for selected_player_type in selected_player_types:
        current_player_instance = None

        if selected_player_type == "RandomPlayer":
            current_player_instance = RandomPlayer()

        if selected_player_type == "RandomFullRangePlayer":
            current_player_instance = RandomFullRangePlayer()

        assert(current_player_instance is not None)
        player_instances.append(current_player_instance)
        if len(player_instances) >= player_count:
            break

    player_controllers = [PlayerController(player_instance) for player_instance in player_instances]

    return player_controllers
