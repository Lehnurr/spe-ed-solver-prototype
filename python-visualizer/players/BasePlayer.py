from abc import abstractmethod


class BasePlayer:
    @abstractmethod
    def handle_step(self, step_info, slice_viewer):
        raise NotImplementedError

    @abstractmethod
    def get_slice_viewer_attributes(self):
        raise NotImplementedError
