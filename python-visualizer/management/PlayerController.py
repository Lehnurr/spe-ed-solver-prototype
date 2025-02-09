from visualisation.SliceViewer import SliceViewer
import time


class PlayerController:

    def __init__(self, player_instance):
        self.playerInstance = player_instance
        self.stepCounter = 0
        self.sliceViewer = None
        self.sliceViewerAttributes = ["game_state"] + player_instance.get_slice_viewer_attributes()

    def handle_step(self, step_info):

        # console logging
        if str(step_info["you"]) == str(list(
                {name: player for name, player in step_info["players"].items() if player["active"]}.keys())[0]):
            print(f"Round {self.playerInstance.roundCounter}:")
        print(f"\tPlayer {step_info['you']}:")
        print(f"\t\treceived info: {step_info}")

        # note start time
        start_time = time.time()

        # create if not exist: SliceViewer of fitting dimensions with initialised attributes
        if not self.sliceViewer:
            self.sliceViewer = SliceViewer(step_info["width"], step_info["height"], self.sliceViewerAttributes)

        # return no action if game is over
        if not step_info["running"]:
            return None

        # return no action if player is dead
        if not step_info["players"][str(step_info["you"])]["active"]:
            return None

        # perform player calculations and receive next action based on step info
        action = self.playerInstance.handle_step(step_info, self.sliceViewer)

        # logging
        self.sliceViewer.add_data("game_state", step_info["cells"])
        self.sliceViewer.next_step()
        print(f"\t\tsent action: {action.name} ({time.time() - start_time:.2f}s)")

        # return result
        return action

    def persist_logging(self):
        self.sliceViewer.persist_viewer_data()
