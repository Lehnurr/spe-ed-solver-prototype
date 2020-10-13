from management import PlayerControllerFactory
import config
from game_connection.InformatiCupConnector import InformatiCupConnector
from game_connection.SimulationConnector import SimulationConnector
from visualisation import SliceViewer
import sys


def start():

    sys.setrecursionlimit(config.RECURSION_LIMIT)

    if config.SIMULATED:
        player_controllers = PlayerControllerFactory.get_player_controllers(config.SELECTED_PLAYER_TYPES,
                                                                            config.SIMULATION_PLAYER_COUNT)
        connector = SimulationConnector(config.SIMULATION_BOARD_WIDTH,
                                        config.SIMULATION_BOARD_HEIGHT,
                                        player_controllers)
        connector.start()

    else:
        player_controller = PlayerControllerFactory.get_player_controllers(config.SELECTED_PLAYER_TYPES, 1)[0]
        connector = InformatiCupConnector(config.URL, config.API_KEY, player_controller)
        connector.start()

    SliceViewer.show_all_viewers()


if __name__ == "__main__":
    start()
