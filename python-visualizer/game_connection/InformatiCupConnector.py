import asyncio
import json
import websockets
from game_connection.BaseConnector import BaseConnector


class InformatiCupConnector(BaseConnector):

    def __init__(self, url: str, key: str, player_controller):
        self.url = url
        self.key = key
        self.playerController = player_controller

    async def __play_loop(self):
        async with websockets.connect(f"{self.url}?key={self.key}") as websocket:
            print("Waiting for initial state...", flush=True)
            while True:
                state_json = await websocket.recv()
                step_info = json.loads(state_json)
                own_player = step_info["players"][str(step_info["you"])]
                if not step_info["running"] or not own_player["active"]:
                    break
                action = self.playerController.handle_step(step_info)
                print(f"\t>{action.name.lower()}")
                action_json = json.dumps({"action": action.name.lower()})
                await websocket.send(action_json)
        self.playerController.persist_logging()

    def start(self):
        asyncio.get_event_loop().run_until_complete(self.__play_loop())
