from players.RandomPlayer import RandomPlayer
from players.RandomFullRangePlayer import RandomFullRangePlayer
from players.EnemyProbabilityFullRangePlayer import EnemyProbabilityFullRangePlayer
from players.MostReachablePointsFullRangePlayer import MostReachablePointsFullRangePlayer
from players.MostReachablePointsWeightedPlayer import MostReachablePointsWeightedPlayer
from players.CorridorCombinedFullRangePlayer import CorridorCombinedFullRangePlayer
from players.CombinedFullRangePlayer import CombinedFullRangePlayer
from management.PlayerController import PlayerController


def get_player_controllers(selected_player_types, player_count):
    player_instances = []

    for selected_player_type in selected_player_types:
        current_player_instance = None

        if selected_player_type == "RandomPlayer":
            current_player_instance = RandomPlayer()

        if selected_player_type == "RandomFullRangePlayer":
            current_player_instance = RandomFullRangePlayer()

        if selected_player_type == "EnemyProbabilityFullRangePlayer":
            current_player_instance = EnemyProbabilityFullRangePlayer()

        if selected_player_type == "MostReachablePointsFullRangePlayer":
            current_player_instance = MostReachablePointsFullRangePlayer()

        if selected_player_type == "MostReachablePointsWeightedPlayer":
            current_player_instance = MostReachablePointsWeightedPlayer()

        if selected_player_type == "CombinedFullRangePlayer":
            current_player_instance = CombinedFullRangePlayer()

        if selected_player_type == "CorridorCombinedFullRangePlayer":
            current_player_instance = CorridorCombinedFullRangePlayer()

        assert(current_player_instance is not None)
        player_instances.append(current_player_instance)
        if len(player_instances) >= player_count:
            break

    player_controllers = [PlayerController(player_instance) for player_instance in player_instances]

    return player_controllers
