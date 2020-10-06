from visualisation.SliceViewer import SliceViewer


class PlayerController:

    def __init__(self, player_instance):
        self.playerInstance = player_instance
        self.stepCounter = 0
        self.sliceViewer = None
        self.sliceViewerAttributes = ["game_state"] + player_instance.get_slice_viewer_attributes()

    def handle_step(self, step_info):

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
        action = self.playerInstance.handle_step(step_info)

        # logging
        self.sliceViewer.add_data("game_state", step_info["cells"])
        self.sliceViewer.next_step()

        # return result
        return action

    def persist_logging(self):
        self.sliceViewer.show_slices()








