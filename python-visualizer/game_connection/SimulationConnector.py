from game_connection.BaseConnector import BaseConnector
from simulation.LocalGameService import LocalGameService
import json


class SimulationConnector(BaseConnector):

    def __init__(self, board_width, board_height, player_controllers):
        self.localGameService = LocalGameService(board_width, board_height, len(player_controllers))
        for player_idx, player_controller in enumerate(player_controllers):
            self.localGameService.on_round_start += \
                self.RoundActionHandler(player_idx + 1, player_controller, self.localGameService).round_action

    def start(self):
        self.localGameService.start()

    class RoundActionHandler:

        def __init__(self, player_id, player_controller, local_game_service):
            self.playerId = player_id
            self.playerController = player_controller
            self.localGameService = local_game_service
            self.counter = 0

        def round_action(self, json_data):
            step_info = json.loads(json_data)
            step_info["you"] = self.playerId
            own_player = step_info["players"][str(self.playerId)]
            if step_info["running"] and own_player["active"]:
                action = self.playerController.handle_step(step_info)
                self.localGameService.do_action(self.playerId, action)
                self.counter += 1
            elif not step_info["running"]:
                self.playerController.persist_logging()





