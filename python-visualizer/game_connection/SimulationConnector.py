from game_connection.BaseConnector import BaseConnector
from simulation.spe_ed_localservice import LocalGameService


class SimulationConnector(BaseConnector):

    def __init__(self, board_width, board_height, player_controllers):
        self.localGameService = LocalGameService(board_width, board_height, len(player_controllers))
        for player_controller in player_controllers:
            self.localGameService.on_round_start += self.__round_action(0)

    def start(self):
        self.localGameService.start()

    def __round_action(self, player_id, json_data={}):
        print(player_id)
        print(json_data)

